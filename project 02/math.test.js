const { add, multiply } = require('./math');
//  test
let failed = 0;
let passed = 0;

function assert(testName, actual, expected) {
  if (actual === expected) {
    console.log(`PASS: ${testName}`);
    passed++;
  } else {
    console.log(`FAIL: ${testName} — expected ${expected}, got ${actual}`);
    failed++;
  }
}

assert('add positive numbers', add(2, 3), 5);
assert('add negative numbers', add(-1, -1), -2);
assert('add zero', add(5, 0), 5);
assert('multiply positive numbers', multiply(3, 4), 12);
assert('multiply by zero', multiply(5, 0), 0);
assert('multiply negative numbers', multiply(-2, 3), -6);

console.log(`\nResults: ${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
