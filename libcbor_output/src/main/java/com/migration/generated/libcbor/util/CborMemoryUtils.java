package com.migration.generated.libcbor.util;

public final class CborMemoryUtils {
    private CborMemoryUtils() {
    }

    public static int safeAdd(int left, int right) {
        return Math.addExact(left, right);
    }

    public static long safeAdd(long left, long right) {
        return Math.addExact(left, right);
    }

    public static int safeMultiply(int left, int right) {
        return Math.multiplyExact(left, right);
    }

    public static long safeMultiply(long left, long right) {
        return Math.multiplyExact(left, right);
    }
}
