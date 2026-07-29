package com.migration.generated.libcbor.internal;

import com.migration.generated.libcbor.model.CborItem;

public final class CborBuilderContext {
    private final CborStack stack = new CborStack();
    private CborItem rootItem;
    private boolean syntaxFailure;
    private boolean buildFailure;

    public CborStack stack() {
        return stack;
    }

    public CborItem rootItem() {
        return rootItem;
    }

    public void setRootItem(CborItem rootItem) {
        this.rootItem = rootItem;
    }

    public boolean syntaxFailure() {
        return syntaxFailure;
    }

    public void setSyntaxFailure(boolean syntaxFailure) {
        this.syntaxFailure = syntaxFailure;
    }

    public boolean buildFailure() {
        return buildFailure;
    }

    public void setBuildFailure(boolean buildFailure) {
        this.buildFailure = buildFailure;
    }
}
