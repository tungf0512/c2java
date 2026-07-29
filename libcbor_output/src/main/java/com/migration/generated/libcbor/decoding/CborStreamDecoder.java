package com.migration.generated.libcbor.decoding;

import com.migration.generated.libcbor.CborDecodeException;
import com.migration.generated.libcbor.model.*;
import com.migration.generated.libcbor.util.CborUnicode;
import java.nio.ByteBuffer;

public final class CborStreamDecoder {
    public CborDecoderResult decode(byte[] data, CborCallbacks callbacks) {
        return decode(ByteBuffer.wrap(data), callbacks);
    }

    public CborDecoderResult decode(ByteBuffer buffer, CborCallbacks callbacks) {
        int start = buffer.position();
        try {
            decodeItem(buffer, callbacks);
            return new CborDecoderResult(CborDecoderStatus.FINISHED, buffer.position() - start);
        } catch (IndexOutOfBoundsException | java.nio.BufferUnderflowException e) {
            return new CborDecoderResult(CborDecoderStatus.NOT_ENOUGH_DATA, Math.max(0, buffer.position() - start));
        }
    }

    private void decodeItem(ByteBuffer buffer, CborCallbacks callbacks) {
        int initial = readUnsignedByte(buffer);
        int major = (initial >>> 5) & 0x7;
        int ai = initial & 0x1F;
        long argument = readArgument(buffer, ai);
        switch (major) {
            case 0 -> callbacks.onUnsignedInteger(argument, widthFor(ai));
            case 1 -> callbacks.onNegativeInteger(argument, widthFor(ai));
            case 2 -> decodeByteString(buffer, callbacks, ai, argument);
            case 3 -> decodeTextString(buffer, callbacks, ai, argument);
            case 4 -> decodeArray(buffer, callbacks, ai, argument);
            case 5 -> decodeMap(buffer, callbacks, ai, argument);
            case 6 -> {
                callbacks.onTag(argument);
                decodeItem(buffer, callbacks);
            }
            case 7 -> decodeSimpleOrFloat(buffer, callbacks, ai, argument);
            default -> throw new CborDecodeException("Invalid major type");
        }
    }

    private void decodeByteString(ByteBuffer buffer, CborCallbacks callbacks, int ai, long argument) {
        if (ai == 31) {
            callbacks.onByteStringStartIndefinite();
            while (peekUnsignedByte(buffer) != 0xFF) {
                decodeItem(buffer, callbacks);
            }
            callbacks.onBreak();
            readUnsignedByte(buffer);
            return;
        }
        byte[] bytes = new byte[(int) argument];
        buffer.get(bytes);
        callbacks.onByteString(bytes);
    }

    private void decodeTextString(ByteBuffer buffer, CborCallbacks callbacks, int ai, long argument) {
        if (ai == 31) {
            callbacks.onTextStringStartIndefinite();
            while (peekUnsignedByte(buffer) != 0xFF) {
                decodeItem(buffer, callbacks);
            }
            callbacks.onBreak();
            readUnsignedByte(buffer);
            return;
        }
        byte[] bytes = new byte[(int) argument];
        buffer.get(bytes);
        callbacks.onTextString(bytes, CborUnicode.validateAndCountCodePoints(bytes));
    }

    private void decodeArray(ByteBuffer buffer, CborCallbacks callbacks, int ai, long argument) {
        if (ai == 31) {
            callbacks.onArrayStartIndefinite();
            while (peekUnsignedByte(buffer) != 0xFF) {
                decodeItem(buffer, callbacks);
            }
            callbacks.onBreak();
            readUnsignedByte(buffer);
            return;
        }
        callbacks.onArrayStart((int) argument);
        for (int index = 0; index < argument; index++) {
            decodeItem(buffer, callbacks);
        }
    }

    private void decodeMap(ByteBuffer buffer, CborCallbacks callbacks, int ai, long argument) {
        if (ai == 31) {
            callbacks.onMapStartIndefinite();
            while (peekUnsignedByte(buffer) != 0xFF) {
                decodeItem(buffer, callbacks);
                decodeItem(buffer, callbacks);
            }
            callbacks.onBreak();
            readUnsignedByte(buffer);
            return;
        }
        callbacks.onMapStart((int) argument);
        for (int index = 0; index < argument; index++) {
            decodeItem(buffer, callbacks);
            decodeItem(buffer, callbacks);
        }
    }

    private void decodeSimpleOrFloat(ByteBuffer buffer, CborCallbacks callbacks, int ai, long argument) {
        switch (ai) {
            case 20 -> callbacks.onBoolean(false);
            case 21 -> callbacks.onBoolean(true);
            case 22 -> callbacks.onNull();
            case 23 -> callbacks.onUndefined();
            case 24 -> callbacks.onSimpleValue((int) argument);
            case 25 -> callbacks.onHalfFloat((int) argument);
            case 26 -> callbacks.onFloat((int) argument);
            case 27 -> callbacks.onDouble(argument);
            case 31 -> callbacks.onBreak();
            default -> callbacks.onSimpleValue(ai);
        }
    }

    private static int readUnsignedByte(ByteBuffer buffer) {
        return buffer.get() & 0xFF;
    }

    private static int peekUnsignedByte(ByteBuffer buffer) {
        return buffer.get(buffer.position()) & 0xFF;
    }

    private static long readArgument(ByteBuffer buffer, int ai) {
        return switch (ai) {
            case 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23 -> ai;
            case 24 -> readUnsignedByte(buffer);
            case 25 -> readUnsignedShort(buffer);
            case 26 -> readUnsignedInt(buffer);
            case 27 -> readUnsignedLong(buffer);
            case 31 -> -1;
            default -> throw new CborDecodeException("Reserved additional information");
        };
    }

    private static long readUnsignedShort(ByteBuffer buffer) {
        return ((long) readUnsignedByte(buffer) << 8) | readUnsignedByte(buffer);
    }

    private static long readUnsignedInt(ByteBuffer buffer) {
        return ((long) readUnsignedShort(buffer) << 16) | readUnsignedShort(buffer);
    }

    private static long readUnsignedLong(ByteBuffer buffer) {
        return ((long) readUnsignedInt(buffer) << 32) | readUnsignedInt(buffer);
    }

    private static CborWidth widthFor(int ai) {
        return switch (ai) {
            case 0, 1, 2, 3, 4, 5, 6, 7 -> CborWidth.ZERO;
            case 24 -> CborWidth.EIGHT;
            case 25 -> CborWidth.SIXTEEN;
            case 26 -> CborWidth.THIRTY_TWO;
            case 27 -> CborWidth.SIXTY_FOUR;
            default -> CborWidth.INDEFINITE;
        };
    }
}
