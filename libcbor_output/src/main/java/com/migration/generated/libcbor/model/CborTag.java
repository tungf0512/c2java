package com.migration.generated.libcbor.model;

public final class CborTag extends CborItem {
    private final long value;
    private CborItem taggedItem;

    public CborTag(long value) {
        if (value < 0) {
            throw new IllegalArgumentException("Tag value must be non-negative");
        }
        this.value = value;
    }

    public long value() {
        return value;
    }

    public CborItem taggedItem() {
        return taggedItem;
    }

    public void setTaggedItem(CborItem taggedItem) {
        if (taggedItem == null) {
            throw new IllegalArgumentException("Tagged item must not be null");
        }
        this.taggedItem = taggedItem;
    }

    @Override
    public CborType type() {
        return CborType.TAG;
    }

    @Override
    public CborItem deepCopy() {
        CborTag copy = new CborTag(value);
        if (taggedItem != null) {
            copy.setTaggedItem(taggedItem.deepCopy());
        }
        return copy;
    }

    @Override
    public CborItem deepCopyDefinite() {
        CborTag copy = new CborTag(value);
        if (taggedItem != null) {
            copy.setTaggedItem(taggedItem.deepCopyDefinite());
        }
        return copy;
    }

    @Override
    public boolean equals(Object obj) {
        return obj instanceof CborTag other && value == other.value && java.util.Objects.equals(taggedItem, other.taggedItem);
    }

    @Override
    public int hashCode() {
        return Long.hashCode(value) * 31 + java.util.Objects.hashCode(taggedItem);
    }
}
