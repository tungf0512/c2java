package com.migration.generated.libcbor.internal;

import com.migration.generated.libcbor.model.CborItem;
import java.util.ArrayDeque;
import java.util.Deque;

public final class CborStack {
    private final Deque<Object> stack = new ArrayDeque<>();

    public void push(Object value) {
        stack.push(value);
    }

    public Object pop() {
        return stack.pop();
    }

    public Object peek() {
        return stack.peek();
    }

    public boolean isEmpty() {
        return stack.isEmpty();
    }
}
