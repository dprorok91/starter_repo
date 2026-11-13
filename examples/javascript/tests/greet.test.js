import test from 'node:test';
import assert from 'node:assert/strict';
import { greet } from '../src/greet.js';

test('greeting trims the name', () => {
  assert.equal(greet(' Ada '), 'Hello, Ada!');
});

test('empty names are rejected', () => {
  assert.throws(() => greet(' '), /required/);
});
