static byte bcd2bin (byte val) { return val - 6 * (val >> 4); }
static byte bin2bcd (byte val) { return val + 6 * (val / 10); }
