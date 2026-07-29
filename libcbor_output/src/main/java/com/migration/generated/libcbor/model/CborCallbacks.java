package com.migration.generated.libcbor.model;

public interface CborCallbacks {
    default void onUnsignedInteger(long value, CborWidth width) {
    }

    default void onNegativeInteger(long encodedMagnitude, CborWidth width) {
    }

    default void onByteString(byte[] data) {
    }

    default void onByteStringStartIndefinite() {
    }

    default void onTextString(byte[] data, int codePointCount) {
    }

    default void onTextStringStartIndefinite() {
    }

    default void onArrayStart(int size) {
    }

    default void onArrayStartIndefinite() {
    }

    default void onMapStart(int size) {
    }

    default void onMapStartIndefinite() {
    }

    default void onTag(long value) {
    }

    default void onSimpleValue(int value) {
    }

    default void onBoolean(boolean value) {
    }

    default void onNull() {
    }

    default void onUndefined() {
    }

    default void onHalfFloat(int bits) {
    }

    default void onFloat(int bits) {
    }

    default void onDouble(long bits) {
    }

    default void onBreak() {
    }
}
