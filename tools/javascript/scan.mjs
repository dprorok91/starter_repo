import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { parse } from '@babel/parser';

const input = JSON.parse(readFileSync(0, 'utf8'));
const rows = input.files.map((file) => {
  const ast = parse(readFileSync(resolve(input.root, file), 'utf8'), {
    sourceType: 'unambiguous', plugins: ['jsx'], errorRecovery: false,
  });
  const symbols = [], imports = [], tests = [];
  function name(node) { return node?.name ?? node?.value ?? ''; }
  function visit(node, parents = [], parent = null) {
    if (!node || typeof node !== 'object') return;
    let scope = parents;
    let declared = '';
    if (['FunctionDeclaration', 'ClassDeclaration'].includes(node.type)) declared = name(node.id);
    if (node.type === 'VariableDeclarator' && ['ArrowFunctionExpression', 'FunctionExpression', 'ClassExpression'].includes(node.init?.type)) declared = name(node.id);
    if (['ClassMethod', 'ClassPrivateMethod', 'ObjectMethod'].includes(node.type)) declared = name(node.key);
    if (declared) {
      const qualified = [...parents, declared].join('.');
      const comments = node.leadingComments ?? parent?.leadingComments ?? [];
      symbols.push({ id: `${file}::${qualified}`, name: qualified, line: node.loc.start.line,
        kind: node.type.includes('ClassDeclaration') ? 'class' : 'function',
        documentation: comments.map(c => c.value.trim()).join('\n') });
      scope = [...parents, declared];
    }
    if (['ImportDeclaration', 'ExportNamedDeclaration', 'ExportAllDeclaration'].includes(node.type) && node.source) imports.push(node.source.value);
    if (node.type === 'CallExpression') {
      const callee = node.callee;
      if (callee?.name === 'require' && node.arguments[0]?.type === 'StringLiteral') imports.push(node.arguments[0].value);
      if (callee?.type === 'Import' && node.arguments[0]?.type === 'StringLiteral') imports.push(node.arguments[0].value);
      // Static literal names only. Dynamic test names remain unclaimed.
      if (['test', 'it'].includes(callee?.name) && node.arguments[0]?.type === 'StringLiteral') tests.push(`${file}::${node.arguments[0].value}`);
    }
    for (const [key, value] of Object.entries(node)) {
      if (['loc', 'start', 'end', 'leadingComments', 'trailingComments', 'innerComments', 'comments', 'tokens', 'extra'].includes(key)) continue;
      if (Array.isArray(value)) value.forEach(child => visit(child, scope, node));
      else if (value && typeof value === 'object') visit(value, scope, node);
    }
  }
  visit(ast);
  return { path: file, symbols, imports: [...new Set(imports)].sort(), tests: [...new Set(tests)].sort() };
});
process.stdout.write(JSON.stringify(rows));
