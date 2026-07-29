package com.migration.generated.libcbor.internal;

import com.migration.generated.libcbor.CborDecodeException;
import com.migration.generated.libcbor.model.*;

public final class CborBuilderCallbacks implements CborCallbacks {
    private final CborBuilderContext context = new CborBuilderContext();

    public CborItem rootItem() {
        return context.rootItem();
    }

    @Override
    public void onUnsignedInteger(long value, CborWidth width) {
        append(new CborUnsignedInteger(value, width));
    }

    @Override
    public void onNegativeInteger(long encodedMagnitude, CborWidth width) {
        append(new CborNegativeInteger(encodedMagnitude, width));
    }

    @Override
    public void onByteString(byte[] data) {
        append(new CborByteString(data));
    }

    @Override
    public void onByteStringStartIndefinite() {
        context.stack().push(new CborByteString());
    }

    @Override
    public void onTextString(byte[] data, int codePointCount) {
        append(new CborTextString(data));
    }

    @Override
    public void onTextStringStartIndefinite() {
        context.stack().push(new CborTextString());
    }

    @Override
    public void onArrayStart(int size) {
        ContainerFrame frame = new ContainerFrame(new CborArray(size), size, false, false);
        if (frame.isComplete()) {
            append(frame.item);
        } else {
            context.stack().push(frame);
        }
    }

    @Override
    public void onArrayStartIndefinite() {
        context.stack().push(new ContainerFrame(new CborArray(), -1, true, false));
    }

    @Override
    public void onMapStart(int size) {
        ContainerFrame frame = new ContainerFrame(new CborMap(size), size * 2, false, true);
        if (frame.isComplete()) {
            append(frame.item);
        } else {
            context.stack().push(frame);
        }
    }

    @Override
    public void onMapStartIndefinite() {
        context.stack().push(new ContainerFrame(new CborMap(), -1, true, true));
    }

    @Override
    public void onTag(long value) {
        context.stack().push(new CborTag(value));
    }

    @Override
    public void onSimpleValue(int value) {
        append(CborFloatOrCtrl.simple(value));
    }

    @Override
    public void onBoolean(boolean value) {
        append(CborFloatOrCtrl.bool(value));
    }

    @Override
    public void onNull() {
        append(CborFloatOrCtrl.nullValue());
    }

    @Override
    public void onUndefined() {
        append(CborFloatOrCtrl.undefined());
    }

    @Override
    public void onHalfFloat(int bits) {
        append(CborFloatOrCtrl.halfFloat(bits));
    }

    @Override
    public void onFloat(int bits) {
        append(CborFloatOrCtrl.singleFloat(bits));
    }

    @Override
    public void onDouble(long bits) {
        append(CborFloatOrCtrl.doubleFloat(bits));
    }

    @Override
    public void onBreak() {
        Object top = context.stack().peek();
        if (top instanceof CborByteString byteString) {
            context.stack().pop();
            append(byteString);
        } else if (top instanceof CborTextString textString) {
            context.stack().pop();
            append(textString);
        } else if (top instanceof ContainerFrame frame && frame.indefinite) {
            context.stack().pop();
            append(frame.item);
        } else {
            throw new CborDecodeException("Unexpected break marker");
        }
    }

    private void append(CborItem item) {
        if (context.stack().isEmpty()) {
            if (context.rootItem() != null) {
                throw new CborDecodeException("Multiple root items encountered");
            }
            context.setRootItem(item);
            return;
        }
        Object top = context.stack().peek();
        if (top instanceof CborTag tag) {
            context.stack().pop();
            tag.setTaggedItem(item);
            append(tag);
            return;
        }
        if (top instanceof CborByteString byteString) {
            if (!(item instanceof CborByteString chunk) || chunk.isIndefinite()) {
                throw new CborDecodeException("Indefinite byte string requires definite byte string chunks");
            }
            byteString.addChunk(chunk);
            return;
        }
        if (top instanceof CborTextString textString) {
            if (!(item instanceof CborTextString chunk) || chunk.isIndefinite()) {
                throw new CborDecodeException("Indefinite text string requires definite text string chunks");
            }
            textString.addChunk(chunk);
            return;
        }
        if (top instanceof ContainerFrame frame) {
            frame.accept(item);
            if (!frame.indefinite && frame.isComplete()) {
                context.stack().pop();
                append(frame.item);
            }
            return;
        }
        throw new CborDecodeException("Unsupported builder stack state");
    }

    private static final class ContainerFrame {
        private final CborItem item;
        private final int expectedEntries;
        private final boolean indefinite;
        private final boolean map;
        private int seenEntries;
        private CborItem pendingKey;

        private ContainerFrame(CborItem item, int expectedEntries, boolean indefinite, boolean map) {
            this.item = item;
            this.expectedEntries = expectedEntries;
            this.indefinite = indefinite;
            this.map = map;
        }

        private void accept(CborItem value) {
            if (!map) {
                ((CborArray) item).add(value);
                seenEntries++;
                return;
            }
            if (pendingKey == null) {
                pendingKey = value;
            } else {
                ((CborMap) item).add(pendingKey, value);
                pendingKey = null;
                seenEntries += 2;
            }
        }

        private boolean isComplete() {
            return expectedEntries >= 0 && seenEntries == expectedEntries && pendingKey == null;
        }
    }
}
