"""
main.py — G.E.M.A.T.R.I.A v2.0
PySide6 GUI — Windows / Blue Archive JP edition.

Usage:
    python main.py

Requirements:
    pip install PySide6 UnityPy Pillow
"""

import os
import sys
import subprocess
import json
from pathlib import Path

import undo_db
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QLabel, QPushButton, QLineEdit, QFileDialog,
    QTableView, QHeaderView, QCheckBox, QScrollArea, QFrame,
    QProgressBar, QTextEdit, QDialog, QAbstractItemView,
    QMessageBox, QStatusBar, QGroupBox, QGridLayout, QInputDialog,
    QSizePolicy, QToolButton, QMenu,
)
from PySide6.QtCore import (
    Qt, QThread, Signal, QSortFilterProxyModel, QAbstractTableModel,
    QModelIndex, QSize, QTimer,
)
from PySide6.QtGui import QColor, QFont, QBrush, QIcon, QPixmap, QPainter

import backend

# ─────────────────────────────────────────────────────────────────────────────
# THEME
# ─────────────────────────────────────────────────────────────────────────────

QSS = """
* { font-family: 'Segoe UI', sans-serif; font-size: 13px; }

QMainWindow, QDialog { background: #12121f; color: #dde1f0; }

QWidget { background: transparent; color: #dde1f0; }

/* ── Scroll areas ── */
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical {
    background: #1c1c30; width: 8px; border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #3a3a5c; border-radius: 4px; min-height: 24px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ── Sidebar / panels ── */
#sidePanel {
    background: #1a1a2e;
    border-right: 1px solid #2a2a44;
}
#detailPanel {
    background: #1a1a2e;
    border-left: 1px solid #2a2a44;
}
#topBar {
    background: #0f0f1e;
    border-bottom: 1px solid #2a2a44;
}

/* ── Table ── */
QTableView {
    background: #12121f;
    alternate-background-color: #181830;
    color: #dde1f0;
    gridline-color: #22223a;
    border: none;
    selection-background-color: #2f4a80;
    selection-color: #e8edff;
    outline: none;
}
QTableView::item { padding: 3px 6px; border: none; }
QTableView::item:hover { background: #1f1f3a; }
QTableView::item:selected { background: #2a3f72; }

QHeaderView { background: #0f0f1e; }
QHeaderView::section {
    background: #0f0f1e;
    color: #7b8dc8;
    padding: 6px 8px;
    border: none;
    border-right: 1px solid #22223a;
    border-bottom: 2px solid #3060c0;
    font-weight: 600;
    font-size: 12px;
    letter-spacing: 0.5px;
}
QHeaderView::section:hover { background: #1a1a30; }

/* ── Buttons ── */
QPushButton {
    background: #22223a;
    color: #c0c8e8;
    border: 1px solid #33335a;
    border-radius: 6px;
    padding: 5px 14px;
    font-weight: 500;
}
QPushButton:hover { background: #2c2c50; border-color: #5577cc; color: #e0e6ff; }
QPushButton:pressed { background: #1a1a30; }
QPushButton:disabled { background: #18182a; color: #44445a; border-color: #22223a; }

QPushButton#accent {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #2a5bd7, stop:1 #4a7ff7);
    color: #ffffff;
    border: none;
    font-weight: 700;
    font-size: 13px;
}
QPushButton#accent:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #3a6de7, stop:1 #5a8fff);
}
QPushButton#accent:pressed { background: #1a40a0; }

QPushButton#scan {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #1e8a5a, stop:1 #28c07a);
    color: #fff;
    border: none;
    font-weight: 700;
    font-size: 13px;
    padding: 5px 18px;
}
QPushButton#scan:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #28a06a, stop:1 #38d08a);
}

QPushButton#danger {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #a02a2a, stop:1 #d04040);
    color: #fff; border: none; font-weight: 700;
}
QPushButton#danger:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #c03030, stop:1 #e05050);
}

/* Version toggle buttons */
QPushButton#verBtn {
    background: #1a1a30;
    color: #7788aa;
    border: 1px solid #2a2a44;
    border-radius: 5px;
    padding: 4px 14px;
    font-weight: 600;
    font-size: 12px;
}
QPushButton#verBtn:checked {
    background: #203060;
    color: #88aaff;
    border-color: #4466cc;
}
QPushButton#verBtn:hover { border-color: #4466cc; }

/* ── Inputs ── */
QLineEdit {
    background: #1a1a2e;
    color: #c8d0ee;
    border: 1px solid #33335a;
    border-radius: 6px;
    padding: 5px 10px;
}
QLineEdit:focus { border-color: #4466dd; }
QLineEdit::placeholder { color: #44445a; }

/* ── Checkboxes ── */
QCheckBox { color: #a0a8c8; spacing: 6px; }
QCheckBox::indicator {
    width: 15px; height: 15px;
    border: 1px solid #44446a;
    border-radius: 3px;
    background: #1a1a30;
}
QCheckBox::indicator:checked {
    background: #3366cc;
    border-color: #4488ff;
    image: none;
}
QCheckBox::indicator:hover { border-color: #5577cc; }

/* ── Group boxes ── */
QGroupBox {
    border: 1px solid #2a2a44;
    border-radius: 6px;
    margin-top: 14px;
    padding: 8px 6px 6px 6px;
    color: #6677aa;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 1px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    left: 10px;
}

/* ── Progress bar ── */
QProgressBar {
    border: 1px solid #2a2a44;
    border-radius: 5px;
    background: #12121f;
    color: #c0c8e8;
    text-align: center;
    font-size: 11px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #2a5bd7, stop:1 #4a9fff);
    border-radius: 4px;
}

/* ── Text edit (log) ── */
QTextEdit {
    background: #0c0c18;
    color: #88ccaa;
    border: 1px solid #22223a;
    border-radius: 5px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}

/* ── Status bar ── */
QStatusBar {
    background: #0a0a16;
    color: #555577;
    border-top: 1px solid #1a1a30;
    font-size: 12px;
}
QStatusBar QLabel { color: #555577; padding: 2px 6px; }

/* ── Splitter ── */
QSplitter::handle { background: #2a2a44; }
QSplitter::handle:horizontal { width: 1px; }

/* ── Info frame ── */
#infoFrame {
    background: #0f0f20;
    border: 1px solid #22223a;
    border-radius: 8px;
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# Tag colour palette — keyed by group / asset_type slug
# ─────────────────────────────────────────────────────────────────────────────

TAG_PALETTE: dict[str, tuple[str, str]] = {
    # (foreground, background)
    "characters":      ("#c8a8ff", "#2a1a4a"),
    "spinecharacters": ("#88b4ff", "#1a2a4a"),
    "spinelobbies":    ("#7de8d0", "#0f2a28"),
    "cafe":            ("#f5d080", "#2a2010"),
    "character":       ("#88e0a0", "#102a18"),
    "fx":              ("#ffaa66", "#2a1800"),
    "other":           ("#8888aa", "#1a1a2a"),
    # asset types
    "textures":             ("#88b4ff", "#10183a"),
    "audio":                ("#88e0a0", "#10281a"),
    "animationclips":       ("#c8a8ff", "#20103a"),
    "animatorcontrollers":  ("#b88ae0", "#1a1030"),
    "materials":            ("#f5d080", "#2a2010"),
    "meshes":               ("#ffaa66", "#281408"),
    "prefabs":              ("#ff8899", "#280a10"),
    "textassets":           ("#7de8d0", "#082820"),
    "timelines":            ("#80d4ff", "#081e28"),
    "assets":               ("#6677aa", "#0e1020"),
}

DEFAULT_TAG = ("#a0a8c8", "#1a1a30")


# ─────────────────────────────────────────────────────────────────────────────
# Tag chip widget
# ─────────────────────────────────────────────────────────────────────────────

class TagChip(QLabel):
    def __init__(self, text: str, slug: str = "", parent=None):
        super().__init__(text, parent)
        fg, bg = TAG_PALETTE.get(slug, DEFAULT_TAG)
        self.setStyleSheet(f"""
            QLabel {{
                background: {bg};
                color: {fg};
                border: 1px solid {fg}44;
                border-radius: 10px;
                padding: 1px 8px;
                font-size: 11px;
                font-weight: 600;
            }}
        """)
        self.setFixedHeight(20)


# ─────────────────────────────────────────────────────────────────────────────
# Section header label
# ─────────────────────────────────────────────────────────────────────────────

def section_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet("""
        color: #4466aa;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.5px;
        padding: 4px 0 2px 0;
    """)
    return lbl


# ─────────────────────────────────────────────────────────────────────────────
# CheckboxFilterGroup — reusable filter widget
# ─────────────────────────────────────────────────────────────────────────────

class CheckboxFilterGroup(QGroupBox):
    changed = Signal(set)

    def __init__(self, title: str, items: list[tuple[str, str]], parent=None):
        super().__init__(title, parent)
        self._cbs: dict[str, QCheckBox] = {}

        layout = QVBoxLayout()
        layout.setSpacing(3)
        layout.setContentsMargins(4, 14, 4, 6)

        # All / None mini-row
        row = QHBoxLayout()
        for label, slot in (("All", self._all), ("None", self._none)):
            btn = QPushButton(label)
            btn.setFixedHeight(20)
            btn.setStyleSheet("font-size: 10px; padding: 0 6px; border-radius: 4px;")
            btn.clicked.connect(slot)
            row.addWidget(btn)
        row.addStretch()
        layout.addLayout(row)

        for key, display in items:
            cb = QCheckBox(display)
            cb.setChecked(True)
            cb.stateChanged.connect(self._emit)
            self._cbs[key] = cb
            layout.addWidget(cb)

        self.setLayout(layout)

    def _emit(self):
        self.changed.emit(self.checked())

    def _all(self):
        for cb in self._cbs.values():
            cb.blockSignals(True); cb.setChecked(True); cb.blockSignals(False)
        self._emit()

    def _none(self):
        for cb in self._cbs.values():
            cb.blockSignals(True); cb.setChecked(False); cb.blockSignals(False)
        self._emit()

    def checked(self) -> set:
        return {k for k, cb in self._cbs.items() if cb.isChecked()}


# ─────────────────────────────────────────────────────────────────────────────
# FilterPanel (left sidebar)
# ─────────────────────────────────────────────────────────────────────────────

class FilterPanel(QWidget):
    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidePanel")
        self.setFixedWidth(220)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        root.addWidget(section_label("SEARCH"))

        self.search = QLineEdit()
        self.search.setPlaceholderText("Character, filename…")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.changed)
        root.addWidget(self.search)

        # Scrollable filter area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        inner = QWidget()
        ivbox = QVBoxLayout(inner)
        ivbox.setSpacing(8)
        ivbox.setContentsMargins(0, 0, 0, 0)

        self.grp_filter = CheckboxFilterGroup("GROUPS", [
            ("characters",      "3D Characters"),
            ("spinecharacters", "Spine Characters"),
            ("spinelobbies",    "Spine Lobbies"),
            ("cafe",            "Café"),
            ("character",       "Story Character"),
            ("fx",              "Effects"),
            ("other",           "Other"),
        ])
        self.grp_filter.changed.connect(self.changed)
        ivbox.addWidget(self.grp_filter)

        self.type_filter = CheckboxFilterGroup("ASSET TYPES", [
            ("textures",            "Textures"),
            ("audio",               "Audio"),
            ("animationclips",      "Animation Clips"),
            ("animatorcontrollers", "Animator Controllers"),
            ("materials",           "Materials"),
            ("meshes",              "Meshes"),
            ("prefabs",             "Prefabs"),
            ("textassets",          "Text Assets"),
            ("timelines",           "Timelines"),
            ("assets",              "Assets (Meta)"),
        ])
        self.type_filter.changed.connect(self.changed)
        ivbox.addWidget(self.type_filter)
        ivbox.addStretch()

        scroll.setWidget(inner)
        root.addWidget(scroll)

    @property
    def search_text(self) -> str:
        return self.search.text()

    @property
    def active_groups(self) -> set:
        return self.grp_filter.checked()

    @property
    def active_types(self) -> set:
        return self.type_filter.checked()


# ─────────────────────────────────────────────────────────────────────────────
# BundleTableModel
# ─────────────────────────────────────────────────────────────────────────────

COLUMNS: list[tuple[str, str]] = [
    ("Character",  "display_name"),
    ("Variant",    "variant"),
    ("Group",      "group_display"),
    ("Asset Type", "asset_type_display"),
    ("Size",       "size"),
    ("Date",       "date"),
    ("Filename",   "filename"),
]

COL_IDX = {key: i for i, (_, key) in enumerate(COLUMNS)}


class BundleTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows: list[dict] = []

    def load(self, bundles: list[dict]):
        self.beginResetModel()
        self._rows = bundles
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._rows)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(COLUMNS)

    def headerData(self, section: int, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return COLUMNS[section][0]

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        row, col = index.row(), index.column()
        if not (0 <= row < len(self._rows)):
            return None

        b    = self._rows[row]
        key  = COLUMNS[col][1]
        val  = b.get(key)

        if role == Qt.DisplayRole:
            if key == "size":
                return backend.format_size(val or 0)
            if key == "variant" and val:
                return val.replace("_", " ").title()
            return str(val) if val else ""

        if role == Qt.ForegroundRole:
            if key == "group_display":
                fg, _ = TAG_PALETTE.get(b.get("group", ""), DEFAULT_TAG)
                return QBrush(QColor(fg))
            if key == "asset_type_display":
                fg, _ = TAG_PALETTE.get(b.get("asset_type", ""), DEFAULT_TAG)
                return QBrush(QColor(fg))
            if key == "display_name":
                return QBrush(QColor("#dde1f0"))

        if role == Qt.UserRole:
            return b

        if role == Qt.ToolTipRole:
            return b.get("filename", "")

    def bundle_at(self, row: int) -> dict | None:
        return self._rows[row] if 0 <= row < len(self._rows) else None

    def all_characters(self) -> list[str]:
        return sorted({b["character"] for b in self._rows if b.get("character")})

    def all_groups(self) -> list[str]:
        return sorted({b["group"] for b in self._rows if b.get("group")})

    def all_types(self) -> list[str]:
        return sorted({b["asset_type"] for b in self._rows if b.get("asset_type")})


# ─────────────────────────────────────────────────────────────────────────────
# BundleProxyModel
# ─────────────────────────────────────────────────────────────────────────────

class BundleProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._search  = ""
        self._groups  : set = set()
        self._types   : set = set()
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.setSortCaseSensitivity(Qt.CaseInsensitive)

    def set_search(self, text: str):
        self._search = text.lower(); self.invalidateFilter()

    def set_groups(self, g: set):
        self._groups = g; self.invalidateFilter()

    def set_types(self, t: set):
        self._types = t; self.invalidateFilter()

    def filterAcceptsRow(self, src_row: int, src_parent: QModelIndex) -> bool:
        m: BundleTableModel = self.sourceModel()
        b = m.bundle_at(src_row)
        if not b:
            return False
        if self._search:
            haystack = " ".join([
                b.get("display_name", ""),
                b.get("character",    ""),
                b.get("variant",      ""),
                b.get("filename",     ""),
            ]).lower()
            if self._search not in haystack:
                return False
        if self._groups and b.get("group") not in self._groups:
            return False
        if self._types and b.get("asset_type") not in self._types:
            return False
        return True

    def get_bundle(self, proxy_row: int) -> dict | None:
        src_idx = self.mapToSource(self.index(proxy_row, 0))
        return self.sourceModel().bundle_at(src_idx.row())


# ─────────────────────────────────────────────────────────────────────────────
# Worker threads
# ─────────────────────────────────────────────────────────────────────────────

class ScanWorker(QThread):
    done  = Signal(list)
    error = Signal(str)

    def __init__(self, path: str):
        super().__init__()
        self.path = path

    def run(self):
        try:
            self.done.emit(backend.scan_bundles(self.path))
        except Exception as e:
            self.error.emit(str(e))


class ExtractWorker(QThread):
    progress = Signal(int, int)
    log      = Signal(str)
    done     = Signal(dict)

    def __init__(self, bundle_path: str, output_dir: str):
        super().__init__()
        self.bundle_path = bundle_path
        self.output_dir  = output_dir

    def run(self):
        self.done.emit(backend.extract_bundle(
            self.bundle_path, self.output_dir,
            progress_cb=lambda v, t: self.progress.emit(v, t),
            log_cb=lambda m: self.log.emit(m),
        ))


class RepackWorker(QThread):
    progress = Signal(int, int)
    log      = Signal(str)
    done     = Signal(dict)

    def __init__(self, input_dir: str, output_path: str):
        super().__init__()
        self.input_dir   = input_dir
        self.output_path = output_path

    def run(self):
        self.done.emit(backend.repack_bundle(
            self.input_dir, self.output_path,
            progress_cb=lambda v, t: self.progress.emit(v, t),
            log_cb=lambda m: self.log.emit(m),
        ))


# ─────────────────────────────────────────────────────────────────────────────
# OperationDialog — shown during extract / repack
# ─────────────────────────────────────────────────────────────────────────────

class OperationDialog(QDialog):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(560, 340)
        self.setStyleSheet("background: #0f0f20;")

        lay = QVBoxLayout(self)
        lay.setSpacing(10)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setFixedHeight(22)
        lay.addWidget(self.bar)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        lay.addWidget(self.log_box)

        self.btn_close = QPushButton("Close")
        self.btn_close.setEnabled(False)
        self.btn_close.clicked.connect(self.accept)
        lay.addWidget(self.btn_close, alignment=Qt.AlignRight)

    def update_progress(self, val: int, total: int):
        if total:
            self.bar.setValue(int(val / total * 100))

    def append_log(self, msg: str):
        self.log_box.append(msg)
        self.log_box.verticalScrollBar().setValue(
            self.log_box.verticalScrollBar().maximum()
        )

    def finish(self, success: bool = True):
        self.bar.setValue(100)
        if success:
            self.append_log("\n✅ Operation complete!")
            self.bar.setStyleSheet(
                "QProgressBar::chunk { background: #28c060; border-radius:4px; }"
            )
        else:
            self.append_log("\n❌ Operation finished with errors.")
            self.bar.setStyleSheet(
                "QProgressBar::chunk { background: #c03030; border-radius:4px; }"
            )
        self.btn_close.setEnabled(True)


# ─────────────────────────────────────────────────────────────────────────────
# DetailPanel (right sidebar)
# ─────────────────────────────────────────────────────────────────────────────

class DetailPanel(QWidget):
    extract_requested = Signal(dict)
    open_dir_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("detailPanel")
        self.setFixedWidth(248)
        self._bundle: dict | None = None
        self._out_dir: str = ""

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        root.addWidget(section_label("BUNDLE DETAILS"))

        # Info frame
        frame = QFrame()
        frame.setObjectName("infoFrame")
        grid = QGridLayout(frame)
        grid.setSpacing(6)
        grid.setContentsMargins(10, 10, 10, 10)

        self._fields: dict[str, QLabel] = {}
        field_defs = [
            ("character", "Character"),
            ("variant",   "Variant"),
            ("group",     "Group"),
            ("type",      "Asset Type"),
            ("size",      "Size"),
            ("date",      "Date"),
            ("hash",      "Hash"),
        ]
        for i, (key, label) in enumerate(field_defs):
            key_lbl = QLabel(label)
            key_lbl.setStyleSheet("color: #445588; font-size: 11px; font-weight: 700;")
            val_lbl = QLabel("—")
            val_lbl.setStyleSheet("color: #a0b0d8; font-size: 12px;")
            val_lbl.setWordWrap(True)
            self._fields[key] = val_lbl
            grid.addWidget(key_lbl, i, 0)
            grid.addWidget(val_lbl, i, 1)

        root.addWidget(frame)

        # Tags
        root.addWidget(section_label("TAGS"))
        self._tags_row = QHBoxLayout()
        self._tags_row.setSpacing(4)
        self._tags_row.setContentsMargins(0, 0, 0, 0)
        tags_w = QWidget()
        tags_w.setLayout(self._tags_row)
        root.addWidget(tags_w)

        # Filename
        root.addWidget(section_label("FILENAME"))
        self._fname_lbl = QLabel("—")
        self._fname_lbl.setWordWrap(True)
        self._fname_lbl.setStyleSheet("""
            color: #44557a;
            font-size: 10px;
            background: #0a0a18;
            border-radius: 4px;
            padding: 5px 6px;
        """)
        root.addWidget(self._fname_lbl)

        root.addStretch()

        # Actions
        self.btn_extract = QPushButton("⬇  Extract Bundle")
        self.btn_extract.setObjectName("accent")
        self.btn_extract.setEnabled(False)
        self.btn_extract.clicked.connect(self._do_extract)
        root.addWidget(self.btn_extract)

        self.btn_open = QPushButton("📁  Open Output Folder")
        self.btn_open.setEnabled(False)
        self.btn_open.clicked.connect(self._do_open)
        root.addWidget(self.btn_open)

    # ── Public ─────────────────────────────────────────────────────────────

    def show_bundle(self, bundle: dict | None, out_dir: str = ""):
        self._bundle  = bundle
        self._out_dir = out_dir

        if not bundle:
            self._clear()
            return

        def v(key: str) -> str:
            val = bundle.get(key)
            if val is None:
                return "—"
            return str(val).replace("_", " ").title()

        self._fields["character"].setText(v("character"))
        self._fields["variant"].setText(v("variant"))
        self._fields["group"].setText(bundle.get("group_display", "—"))
        self._fields["type"].setText(bundle.get("asset_type_display", "—"))
        self._fields["size"].setText(backend.format_size(bundle.get("size", 0)))
        self._fields["date"].setText(bundle.get("date", "—"))
        self._fields["hash"].setText(bundle.get("hash", "—"))
        self._fname_lbl.setText(bundle.get("filename", "—"))

        # Tags
        self._clear_tags()
        for tag in bundle.get("tags", []):
            chip = TagChip(tag, slug=tag)
            self._tags_row.addWidget(chip)
        self._tags_row.addStretch()

        self.btn_extract.setEnabled(True)
        self.btn_open.setEnabled(bool(out_dir) and os.path.isdir(out_dir))

    def refresh_open_btn(self, out_dir: str):
        self._out_dir = out_dir
        self.btn_open.setEnabled(bool(out_dir) and os.path.isdir(out_dir))

    # ── Private ────────────────────────────────────────────────────────────

    def _clear(self):
        for lbl in self._fields.values():
            lbl.setText("—")
        self._fname_lbl.setText("—")
        self._clear_tags()
        self.btn_extract.setEnabled(False)
        self.btn_open.setEnabled(False)

    def _clear_tags(self):
        while self._tags_row.count():
            item = self._tags_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _do_extract(self):
        if self._bundle:
            self.extract_requested.emit(self._bundle)

    def _do_open(self):
        if self._out_dir and os.path.isdir(self._out_dir):
            os.startfile(self._out_dir)

# ─────────────────────────────────────────────────────────────────────────────
# CompressionDialog
# ─────────────────────────────────────────────────────────────────────────────

class CompressionDialog(QDialog):
    """Let the user choose archive format + level before adding to undo DB."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Compression Options")
        self.setModal(True)
        self.setFixedSize(320, 240)

        self._fmt   = "tar.gz"
        self._level = "max"

        lay = QVBoxLayout(self)
        lay.setSpacing(12)
        lay.setContentsMargins(18, 16, 18, 16)

        lay.addWidget(section_label("ARCHIVE FORMAT"))
        fmt_grp = QGroupBox()
        fmt_lay = QHBoxLayout(fmt_grp)
        fmt_lay.setContentsMargins(6, 10, 6, 6)
        fmt_lay.setSpacing(6)

        self._fmt_btns: dict[str, QPushButton] = {}
        for f in undo_db.SUPPORTED_FORMATS:
            btn = QPushButton(f)
            btn.setObjectName("verBtn")
            btn.setCheckable(True)
            btn.setChecked(f == "tar.gz")
            btn.clicked.connect(lambda _, ff=f: self._pick_fmt(ff))
            self._fmt_btns[f] = btn
            fmt_lay.addWidget(btn)
        lay.addWidget(fmt_grp)

        lay.addWidget(section_label("COMPRESSION LEVEL"))
        lvl_grp = QGroupBox()
        lvl_lay = QHBoxLayout(lvl_grp)
        lvl_lay.setContentsMargins(6, 10, 6, 6)
        lvl_lay.setSpacing(6)

        self._lvl_btns: dict[str, QPushButton] = {}
        for lv, lbl in (("min", "🐇  Min (fast)"), ("max", "🐢  Max (small)")):
            btn = QPushButton(lbl)
            btn.setObjectName("verBtn")
            btn.setCheckable(True)
            btn.setChecked(lv == "max")
            btn.clicked.connect(lambda _, ll=lv: self._pick_level(ll))
            self._lvl_btns[lv] = btn
            lvl_lay.addWidget(btn)
        lay.addWidget(lvl_grp)

        lay.addStretch()

        row = QHBoxLayout()
        row.setSpacing(8)
        ok_btn = QPushButton("Confirm")
        ok_btn.setObjectName("accent")
        ok_btn.setFixedHeight(32)
        ok_btn.clicked.connect(self.accept)
        cancel = QPushButton("Cancel")
        cancel.setFixedHeight(32)
        cancel.clicked.connect(self.reject)
        row.addStretch()
        row.addWidget(cancel)
        row.addWidget(ok_btn)
        lay.addLayout(row)

    def _pick_fmt(self, fmt: str):
        self._fmt = fmt
        for f, btn in self._fmt_btns.items():
            btn.setChecked(f == fmt)

    def _pick_level(self, level: str):
        self._level = level
        for lv, btn in self._lvl_btns.items():
            btn.setChecked(lv == level)

    @property
    def fmt(self) -> str:
        return self._fmt

    @property
    def level(self) -> str:
        return self._level


# ─────────────────────────────────────────────────────────────────────────────
# Worker threads for undo DB operations
# ─────────────────────────────────────────────────────────────────────────────

class DbAddWorker(QThread):
    """Hash + compress + write DB entry in background."""
    progress = Signal(int, int)
    log      = Signal(str)
    done     = Signal(object)   # dict | None

    def __init__(self, description: str, source: str, paths: list[str],
                 fmt: str, level: str):
        super().__init__()
        self.description = description
        self.source      = source
        self.paths       = paths
        self.fmt         = fmt
        self.level       = level

    def run(self):
        entry = undo_db.add_entry(
            self.description, self.source, self.paths, self.fmt, self.level,
            log_cb=lambda m: self.log.emit(m),
            progress_cb=lambda v, t: self.progress.emit(v, t),
        )
        self.done.emit(entry)


class RestoreWorker(QThread):
    progress = Signal(int, int)
    log      = Signal(str)
    done     = Signal(bool)

    def __init__(self, entry_id: str):
        super().__init__()
        self.entry_id = entry_id

    def run(self):
        ok = undo_db.restore_entry(
            self.entry_id,
            log_cb=lambda m: self.log.emit(m),
            progress_cb=lambda v, t: self.progress.emit(v, t),
        )
        self.done.emit(ok)


class SideloadWorker(QThread):
    """Copy repacked bundle over the original game bundle."""
    progress = Signal(int, int)
    log      = Signal(str)
    done     = Signal(bool, str)

    def __init__(self, original_path: str, repacked_path: str):
        super().__init__()
        self.original_path = original_path
        self.repacked_path = repacked_path

    def run(self):
        import shutil as _shutil

        self.log.emit(f"Copying to game directory…")
        self.progress.emit(0, 1)
        try:
            _shutil.copy2(self.repacked_path, self.original_path)
            self.progress.emit(1, 1)
            self.log.emit(
                f"✔ Installed: {os.path.basename(self.repacked_path)}\n"
                f"  → {self.original_path}"
            )
            self.done.emit(True, "Installation successful.")
        except Exception as e:
            self.done.emit(False, f"Copy failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# UndoEntryModel — table model for DB entries
# ─────────────────────────────────────────────────────────────────────────────

_UNDO_COLS = [
    ("Timestamp",    "timestamp"),
    ("Description",  "description"),
    ("Source",       "source"),
    ("Format",       "format"),
    ("Level",        "level"),
    ("Files",        "file_count"),
    ("Original",     "size_original"),
    ("Compressed",   "size_compressed"),
]


class UndoEntryModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows: list[dict] = []

    def reload(self):
        self.beginResetModel()
        self._rows = undo_db.list_entries()
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._rows)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(_UNDO_COLS)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return _UNDO_COLS[section][0]

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        row, col = index.row(), index.column()
        if not (0 <= row < len(self._rows)):
            return None
        e   = self._rows[row]
        key = _UNDO_COLS[col][1]
        val = e.get(key)

        if role == Qt.DisplayRole:
            if key == "timestamp":
                try:
                    return datetime.fromisoformat(val).strftime("%Y-%m-%d  %H:%M")
                except Exception:
                    return str(val)
            if key in ("size_original", "size_compressed"):
                return undo_db.fmt_size(val or 0)
            if key == "source":
                return "🖥  App" if val == "app" else "✋  Manual"
            return str(val) if val is not None else "—"

        if role == Qt.ForegroundRole:
            if key == "source":
                c = "#88b4ff" if e.get("source") == "app" else "#88e0a0"
                return QBrush(QColor(c))
            if key == "format":
                return QBrush(QColor("#f5d080"))
            if key == "description":
                return QBrush(QColor("#dde1f0"))

        if role == Qt.UserRole:
            return e

        return None

    def entry_at(self, row: int) -> dict | None:
        return self._rows[row] if 0 <= row < len(self._rows) else None


# ─────────────────────────────────────────────────────────────────────────────
# UndoPanel — the full "Undo / History" tab widget
# ─────────────────────────────────────────────────────────────────────────────

class UndoPanel(QWidget):
    """
    Full-panel widget shown in the Undo/History tab.
    Exposes:
      • add_paths_dialog()   — manually add files/folders
      • add_entry_silent()   — called programmatically (after sideload)
    """
    def __init__(self, workers_ref: list, parent=None):
        super().__init__(parent)
        self._workers = workers_ref
        self._build_ui()
        self.model.reload()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 8, 10, 8)
        root.setSpacing(6)

        # ── toolbar row ─────────────────────────────────────────────────
        trow = QHBoxLayout()
        trow.setSpacing(6)

        lbl = QLabel("RESTORE POINTS")
        lbl.setStyleSheet("color:#4466aa; font-size:10px; font-weight:700; letter-spacing:1px;")
        trow.addWidget(lbl)
        trow.addStretch()

        self._btn_add_files = QPushButton("➕  Add Files…")
        self._btn_add_files.setFixedHeight(27)
        self._btn_add_files.clicked.connect(self._add_files)
        trow.addWidget(self._btn_add_files)

        self._btn_add_dir = QPushButton("📁  Add Folder…")
        self._btn_add_dir.setFixedHeight(27)
        self._btn_add_dir.clicked.connect(self._add_folder)
        trow.addWidget(self._btn_add_dir)

        self._btn_restore = QPushButton("↩  Restore Selected")
        self._btn_restore.setObjectName("accent")
        self._btn_restore.setFixedHeight(27)
        self._btn_restore.setEnabled(False)
        self._btn_restore.clicked.connect(self._restore_selected)
        trow.addWidget(self._btn_restore)

        self._btn_delete = QPushButton("🗑  Delete")
        self._btn_delete.setObjectName("danger")
        self._btn_delete.setFixedHeight(27)
        self._btn_delete.setEnabled(False)
        self._btn_delete.clicked.connect(self._delete_selected)
        trow.addWidget(self._btn_delete)

        self._btn_refresh = QPushButton("⟳")
        self._btn_refresh.setFixedSize(27, 27)
        self._btn_refresh.setToolTip("Refresh list")
        self._btn_refresh.clicked.connect(self.model.reload if hasattr(self, "model") else lambda: None)
        trow.addWidget(self._btn_refresh)

        root.addLayout(trow)

        # ── table ────────────────────────────────────────────────────────
        self.model = UndoEntryModel()
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(26)
        self.table.setFrameShape(QFrame.NoFrame)
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.Interactive)
        hh.setStretchLastSection(False)
        hh.setMinimumSectionSize(60)
        for col, w in enumerate([140, 280, 90, 90, 60, 50, 90, 90]):
            self.table.setColumnWidth(col, w)

        self.table.selectionModel().selectionChanged.connect(self._on_sel)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._context_menu)
        root.addWidget(self.table, 1)

        # ── log area (operation output) ──────────────────────────────────
        root.addWidget(section_label("OPERATION LOG"))
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setFixedHeight(130)
        root.addWidget(self._log)

        # wire refresh button after model exists
        self._btn_refresh.clicked.disconnect()
        self._btn_refresh.clicked.connect(self._do_refresh)

    # ── helpers ──────────────────────────────────────────────────────────

    def _do_refresh(self):
        self.model.reload()

    def _log_append(self, msg: str):
        self._log.append(msg)
        self._log.verticalScrollBar().setValue(self._log.verticalScrollBar().maximum())

    def _log_clear(self):
        self._log.clear()

    def _on_sel(self, *_):
        has = bool(self.table.selectionModel().selectedRows())
        self._btn_restore.setEnabled(has)
        self._btn_delete.setEnabled(has)

    def _selected_entry(self) -> dict | None:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        return self.model.entry_at(rows[0].row())

    def _context_menu(self, pos):
        """Right-click menu on the undo table."""
        entry = self._selected_entry()
        if not entry:
            return
        menu = QMenu(self)
        act_restore = menu.addAction("↩  Restore (undo mod)")
        act_info    = menu.addAction("ℹ  Show original paths")
        menu.addSeparator()
        act_delete  = menu.addAction("🗑  Delete restore point")

        action = menu.exec(self.table.viewport().mapToGlobal(pos))
        if action == act_restore:
            self._restore_selected()
        elif action == act_info:
            paths = "\n".join(entry.get("original_paths", []))
            QMessageBox.information(
                self, "Original Paths",
                f"Snapshot: {entry['description']}\n\nOriginal file(s):\n{paths}"
            )
        elif action == act_delete:
            self._delete_selected()

    # ── Add (manual) ─────────────────────────────────────────────────────

    def _add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Files to Snapshot", "",
            "All Files (*)",
        )
        if paths:
            self._run_add(paths, "manual")

    def _add_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder to Snapshot", "")
        if path:
            self._run_add([path], "manual")

    def _run_add(self, paths: list[str], source: str):
        dlg = CompressionDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return

        desc, ok = QInputDialog.getText(
            self, "Describe this snapshot",
            "Label (optional):",
            text=f"Manual snapshot — {os.path.basename(paths[0])}",
        )
        if not ok:
            return

        self._log_clear()
        self._log_append(f"Adding {len(paths)} path(s) [{dlg.fmt} / {dlg.level}]…")
        self._set_busy(True)

        w = DbAddWorker(desc or "Manual snapshot", source, paths, dlg.fmt, dlg.level)
        w.log.connect(self._log_append)
        w.done.connect(self._on_add_done)
        w.finished.connect(lambda: self._workers.remove(w) if w in self._workers else None)
        self._workers.append(w)
        w.start()

    def _on_add_done(self, entry):
        self._set_busy(False)
        if entry:
            self._log_append(f"\n✅ Snapshot ID: {entry['id'][:8]}…")
        else:
            self._log_append("\n❌ Snapshot failed.")
        self.model.reload()

    # ── Restore ──────────────────────────────────────────────────────────

    def _restore_selected(self):
        entry = self._selected_entry()
        if not entry:
            return
        ans = QMessageBox.question(
            self, "Confirm Restore",
            f"Restore:\n  {entry['description']}\n  [{entry['timestamp'][:16]}]\n\n"
            "This will overwrite the original file(s). Continue?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if ans != QMessageBox.Yes:
            return

        self._log_clear()
        self._log_append(f"Restoring: {entry['description']}…")
        self._set_busy(True)

        w = RestoreWorker(entry["id"])
        w.log.connect(self._log_append)
        w.done.connect(self._on_restore_done)
        w.finished.connect(lambda: self._workers.remove(w) if w in self._workers else None)
        self._workers.append(w)
        w.start()

    def _on_restore_done(self, success: bool):
        self._set_busy(False)
        if not success:
            QMessageBox.warning(self, "Restore", "Restore finished with errors. Check the log.")

    # ── Delete ────────────────────────────────────────────────────────────

    def _delete_selected(self):
        entry = self._selected_entry()
        if not entry:
            return
        ans = QMessageBox.question(
            self, "Delete Snapshot",
            f"Delete restore point:\n  {entry['description']}\n\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if ans != QMessageBox.Yes:
            return
        undo_db.remove_entry(entry["id"])
        self.model.reload()
        self._log_append(f"Deleted: {entry['id'][:8]}…")

    # ── Busy state ────────────────────────────────────────────────────────

    def _set_busy(self, busy: bool):
        for w in (self._btn_add_files, self._btn_add_dir,
                  self._btn_restore, self._btn_delete):
            w.setEnabled(not busy)

    # ── Public API (called from MainWindow) ──────────────────────────────

    def reload(self):
        self.model.reload()


# ─────────────────────────────────────────────────────────────────────────────
# Helper: Find snapshot for a given file
# ─────────────────────────────────────────────────────────────────────────────

def _find_snapshot_for(file_path: str) -> dict | None:
    """
    Return the most recent undo DB entry whose original_paths includes
    file_path (case-insensitive, normalised).  None if not found.
    """
    norm = os.path.normcase(os.path.abspath(file_path))
    for entry in undo_db.list_entries():
        for p in entry.get("original_paths", []):
            if os.path.normcase(os.path.abspath(p)) == norm:
                return entry
    return None


# ─────────────────────────────────────────────────────────────────────────────
# MainWindow
# ─────────────────────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("G.E.M.A.T.R.I.A  —  Graphical Environment & Modding Architecture for Total Resource Intervention & Analysis")
        self.setMinimumSize(1200, 680)
        self.resize(1440, 820)

        self._bundles:  list[dict] = []
        self._version:  str        = "JP"
        self._out_base: str        = backend.DEFAULT_OUTPUT_BASE
        self._workers:  list       = []   # keep refs to prevent GC
        self._undo_panel: UndoPanel | None = None

        self._build_ui()
        self.setStyleSheet(QSS)

    # ── UI construction ────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        vbox = QVBoxLayout(central)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        vbox.addWidget(self._build_topbar())

        # Main area
        split = QSplitter(Qt.Horizontal)
        split.setHandleWidth(1)

        self.filter_panel = FilterPanel()
        self.filter_panel.changed.connect(self._apply_filters)
        split.addWidget(self.filter_panel)

        split.addWidget(self._build_center())

        self.detail_panel = DetailPanel()
        self.detail_panel.extract_requested.connect(self._extract_bundle)
        split.addWidget(self.detail_panel)

        split.setSizes([220, 980, 248])
        split.setStretchFactor(1, 1)
        vbox.addWidget(split, 1)

        # Status bar
        sb = QStatusBar()
        self.setStatusBar(sb)
        self._status = QLabel("Ready — scan a bundle directory to begin.")
        sb.addWidget(self._status)

        self._count_lbl = QLabel("")
        self._count_lbl.setStyleSheet("color: #445577; font-size: 12px; padding: 0 10px;")
        sb.addPermanentWidget(self._count_lbl)

        btn_repack = QPushButton("📦  Repack from Extracted Folder…")
        btn_repack.clicked.connect(self._repack_dialog)
        sb.addPermanentWidget(btn_repack)

    def _build_topbar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("topBar")
        bar.setFixedHeight(58)

        lay = QHBoxLayout(bar)
        lay.setContentsMargins(14, 0, 14, 0)
        lay.setSpacing(10)

        # Title
        title = QLabel("🎮  G.E.M.A.T.R.I.A")
        title.setStyleSheet("color: #5588ee; font-size: 16px; font-weight: 700; letter-spacing: -0.5px;")
        lay.addWidget(title)

        ver_lbl = QLabel("v2.0")
        ver_lbl.setStyleSheet("color: #33446a; font-size: 12px;")
        lay.addWidget(ver_lbl)

        lay.addSpacing(18)

        # Version toggle
        ver_frame = QFrame()
        ver_frame.setStyleSheet("border: 1px solid #2a2a44; border-radius: 6px; background: #111128;")
        ver_lay = QHBoxLayout(ver_frame)
        ver_lay.setContentsMargins(4, 2, 4, 2)
        ver_lay.setSpacing(2)

        self.btn_jp = QPushButton("🇯🇵  JP")
        self.btn_jp.setObjectName("verBtn")
        self.btn_jp.setCheckable(True)
        self.btn_jp.setChecked(True)
        self.btn_jp.clicked.connect(lambda: self._set_version("JP"))
        ver_lay.addWidget(self.btn_jp)

        self.btn_gl = QPushButton("🌐  GL")
        self.btn_gl.setObjectName("verBtn")
        self.btn_gl.setCheckable(True)
        self.btn_gl.setChecked(False)
        self.btn_gl.clicked.connect(lambda: self._set_version("GL"))
        ver_lay.addWidget(self.btn_gl)
        lay.addWidget(ver_frame)

        lay.addSpacing(10)

        # Bundle path
        path_lbl = QLabel("Bundle Path:")
        path_lbl.setStyleSheet("color: #445577; font-size: 12px;")
        lay.addWidget(path_lbl)

        self.path_input = QLineEdit(backend.JP_BUNDLE_PATH)
        self.path_input.setMinimumWidth(340)
        lay.addWidget(self.path_input)

        btn_browse = QPushButton("…")
        btn_browse.setFixedWidth(32)
        btn_browse.clicked.connect(self._browse_path)
        lay.addWidget(btn_browse)

        self.btn_scan = QPushButton("🔍  Scan")
        self.btn_scan.setObjectName("scan")
        self.btn_scan.setFixedHeight(34)
        self.btn_scan.clicked.connect(self._scan)
        lay.addWidget(self.btn_scan)

        lay.addSpacing(14)

        # Output path
        out_lbl = QLabel("Output:")
        out_lbl.setStyleSheet("color: #445577; font-size: 12px;")
        lay.addWidget(out_lbl)

        self.out_input = QLineEdit(self._out_base)
        self.out_input.setMinimumWidth(220)
        self.out_input.textChanged.connect(lambda t: setattr(self, "_out_base", t))
        lay.addWidget(self.out_input)

        btn_out = QPushButton("…")
        btn_out.setFixedWidth(32)
        btn_out.clicked.connect(self._browse_out)
        lay.addWidget(btn_out)

        lay.addStretch()

        return bar

    def _build_center(self) -> QWidget:
        """
        Returns a QTabWidget with:
          Tab 0 — BUNDLES  (original table view)
          Tab 1 — UNDO / HISTORY
        """
        from PySide6.QtWidgets import QTabWidget

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: #111128;
                color: #445577;
                border: 1px solid #1e1e38;
                border-bottom: none;
                padding: 5px 18px;
                font-size: 12px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background: #1a1a2e;
                color: #88aaff;
                border-color: #2a2a50;
                border-bottom: 2px solid #3060c0;
            }
            QTabBar::tab:hover:!selected { background: #181830; }
        """)

        # ── Tab 0: Bundles ────────────────────────────────────────────────────
        bundles_w = QWidget()
        vbox = QVBoxLayout(bundles_w)
        vbox.setContentsMargins(6, 6, 6, 0)
        vbox.setSpacing(4)

        trow = QHBoxLayout()
        trow.setSpacing(6)
        self._table_label = QLabel("BUNDLES")
        self._table_label.setStyleSheet(
            "color:#4466aa; font-size:10px; font-weight:700; letter-spacing:1px;"
        )
        trow.addWidget(self._table_label)
        trow.addStretch()

        btn_sel_all = QPushButton("Select All")
        btn_sel_all.setFixedHeight(26)
        btn_sel_all.setStyleSheet("font-size:11px; padding:0 10px;")
        btn_sel_all.clicked.connect(self._select_all)
        trow.addWidget(btn_sel_all)

        btn_ext_sel = QPushButton("⬇  Extract Selected")
        btn_ext_sel.setObjectName("accent")
        btn_ext_sel.setFixedHeight(26)
        btn_ext_sel.setStyleSheet(
            "font-size:11px; padding:0 12px;"
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #2a5bd7,stop:1 #4a7ff7);"
            "color:#fff; border:none; border-radius:5px; font-weight:700;"
        )
        btn_ext_sel.clicked.connect(self._extract_selected)
        trow.addWidget(btn_ext_sel)
        vbox.addLayout(trow)

        self.model = BundleTableModel()
        self.proxy = BundleProxyModel()
        self.proxy.setSourceModel(self.model)

        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setSortingEnabled(True)
        self.table.setShowGrid(True)
        self.table.setWordWrap(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(26)
        self.table.setFrameShape(QFrame.NoFrame)

        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.Interactive)
        hh.setStretchLastSection(True)
        hh.setMinimumSectionSize(60)
        for col, width in enumerate([160, 130, 140, 140, 80, 90]):
            self.table.setColumnWidth(col, width)

        self.table.selectionModel().selectionChanged.connect(self._on_sel_changed)
        self.table.doubleClicked.connect(self._on_double_click)
        vbox.addWidget(self.table)

        tabs.addTab(bundles_w, "🎮  Bundles")

        # ── Tab 1: Undo / History ─────────────────────────────────────────────
        self._undo_panel = UndoPanel(self._workers)
        tabs.addTab(self._undo_panel, "↩  Undo / History")

        return tabs

    # ── Version / path ─────────────────────────────────────────────────────

    def _set_version(self, ver: str):
        self._version = ver
        self.btn_jp.setChecked(ver == "JP")
        self.btn_gl.setChecked(ver == "GL")
        path = backend.JP_BUNDLE_PATH if ver == "JP" else backend.GL_BUNDLE_PATH
        self.path_input.setText(path)
        label = "Blue Archive JP" if ver == "JP" else "Blue Archive GL"
        self.setWindowTitle(f"G.E.M.A.T.R.I.A  —  {label}")

    def _browse_path(self):
        d = QFileDialog.getExistingDirectory(self, "Select Bundle Directory", self.path_input.text())
        if d:
            self.path_input.setText(d)

    def _browse_out(self):
        d = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.out_input.text())
        if d:
            self.out_input.setText(d)
            self._out_base = d

    # ── Scanning ───────────────────────────────────────────────────────────

    def _scan(self):
        path = self.path_input.text().strip()
        if not os.path.isdir(path):
            QMessageBox.warning(self, "Invalid Path", f"Directory not found:\n{path}")
            return

        self.btn_scan.setEnabled(False)
        self.btn_scan.setText("Scanning…")
        self._set_status("Scanning bundles…")

        w = ScanWorker(path)
        w.done.connect(self._on_scan_done)
        w.error.connect(self._on_scan_err)
        w.finished.connect(lambda: self._workers.remove(w) if w in self._workers else None)
        self._workers.append(w)
        w.start()

    def _on_scan_done(self, bundles: list[dict]):
        self._bundles = bundles
        self.model.load(bundles)
        self._apply_filters()
        self.btn_scan.setEnabled(True)
        self.btn_scan.setText("🔍  Scan")
        self._set_status(f"Loaded {len(bundles)} bundles  ·  {self.path_input.text()}")

    def _on_scan_err(self, msg: str):
        self.btn_scan.setEnabled(True)
        self.btn_scan.setText("🔍  Scan")
        QMessageBox.critical(self, "Scan Error", msg)

    # ── Filters ────────────────────────────────────────────────────────────

    def _apply_filters(self):
        self.proxy.set_search(self.filter_panel.search_text)
        self.proxy.set_groups(self.filter_panel.active_groups)
        self.proxy.set_types(self.filter_panel.active_types)
        self._update_count()

    def _update_count(self):
        vis  = self.proxy.rowCount()
        tot  = self.model.rowCount()
        self._count_lbl.setText(f"{vis} / {tot}")

    # ── Selection ──────────────────────────────────────────────────────────

    def _on_sel_changed(self, *_):
        rows = self.table.selectionModel().selectedRows()
        if len(rows) == 1:
            b = self.proxy.get_bundle(rows[0].row())
            if b:
                out = self._out_dir_for(b)
                self.detail_panel.show_bundle(b, out)
        else:
            self.detail_panel.show_bundle(None)

    def _on_double_click(self, idx):
        b = self.proxy.get_bundle(idx.row())
        if b:
            self._extract_bundle(b)

    def _select_all(self):
        self.table.selectAll()

    # ── Output directory helper ────────────────────────────────────────────

    def _out_dir_for(self, bundle: dict) -> str:
        """Output folder = bundle filename without .bundle — one-to-one mapping."""
        name = os.path.splitext(bundle.get("filename", "unknown"))[0]
        return os.path.join(self._out_base, name)

    # ── Extraction ─────────────────────────────────────────────────────────

    def _extract_bundle(self, bundle: dict):
        out = self._out_dir_for(bundle)
        dlg = OperationDialog(f"Extracting — {bundle.get('display_name', '')}  [{bundle.get('asset_type_display','')}]", self)
        dlg.append_log(f"Bundle : {bundle['filename']}")
        dlg.append_log(f"Output : {out}\n")

        w = ExtractWorker(bundle["path"], out)
        w.progress.connect(dlg.update_progress)
        w.log.connect(dlg.append_log)
        w.done.connect(lambda r: self._on_extract_done(r, dlg, bundle, out))
        w.finished.connect(lambda: self._workers.remove(w) if w in self._workers else None)
        self._workers.append(w)
        w.start()
        dlg.exec()

    def _on_extract_done(self, result: dict, dlg: OperationDialog, bundle: dict, out: str):
        dlg.finish(result["success"])
        if result["success"]:
            s = result.get("stats", {})
            dlg.append_log(
                f"Extracted: {s.get('extracted', 0)}  ·  "
                f"Skipped: {s.get('skipped', 0)}  ·  "
                f"Errors: {s.get('errors', 0)}"
            )
            self.detail_panel.refresh_open_btn(out)
            
            # ── Auto-snapshot original bundle → undo DB ──────────────────────
            # Runs in background; user sees status bar update, no blocking dialog.
            self._auto_snapshot_bundle(bundle)
        else:
            dlg.append_log(f"Error: {result['message']}")

    def _auto_snapshot_bundle(self, bundle: dict):
        """
        Silently compress the original .bundle into the undo DB right after
        extraction. Uses tar.gz/max as default — no dialog, no blocking.
        Batch extraction calls this too (see _batch_next).
        """
        bpath = bundle.get("path", "")
        if not bpath or not os.path.isfile(bpath):
            self._set_status("⚠ Restore point skipped — bundle path missing.")
            return

        display = bundle.get("display_name", bundle.get("filename", "?"))
        desc    = f"Pre-edit snapshot — {bundle.get('filename', '?')}"
        self._set_status(f"Saving restore point for {display}…")

        w = DbAddWorker(desc, "app", [bpath], "tar.gz", "max")
        w.log.connect(lambda m: None)          # silent — no dialog
        w.done.connect(lambda entry: self._on_auto_snapshot_done(entry, display))
        w.finished.connect(lambda: self._workers.remove(w) if w in self._workers else None)
        self._workers.append(w)
        w.start()

    def _on_auto_snapshot_done(self, entry, display_name: str):
        if entry:
            self._set_status(f"✅ Restore point saved — {display_name}")
            if self._undo_panel:
                self._undo_panel.reload()
        else:
            self._set_status("⚠ Restore point failed — check the Undo/History tab.")

    def _extract_selected(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, "No Selection", "Select one or more bundles first.")
            return
        bundles = [b for r in rows if (b := self.proxy.get_bundle(r.row()))]
        if len(bundles) == 1:
            self._extract_bundle(bundles[0])
            return

        ans = QMessageBox.question(
            self, "Batch Extract",
            f"Extract {len(bundles)} bundles?\nThey will be saved under:\n{self._out_base}",
            QMessageBox.Yes | QMessageBox.No,
        )
        if ans != QMessageBox.Yes:
            return
        self._batch_idx   = 0
        self._batch_list  = bundles
        self._batch_ok    = 0
        self._batch_fail  = 0
        self._batch_next()

    def _batch_next(self):
        if self._batch_idx >= len(self._batch_list):
            QMessageBox.information(
                self, "Batch Complete",
                f"Done!  ✅ {self._batch_ok}  ❌ {self._batch_fail}"
                f"  out of {len(self._batch_list)} bundles.",
            )
            return

        b   = self._batch_list[self._batch_idx]
        out = self._out_dir_for(b)
        self._set_status(
            f"Extracting {self._batch_idx + 1}/{len(self._batch_list)}: {b['display_name']}…"
        )

        w = ExtractWorker(b["path"], out)

        def on_done(result):
            if result["success"]:
                self._batch_ok += 1
                self._auto_snapshot_bundle(b)   # ← snapshot each bundle
            else:
                self._batch_fail += 1
            self._batch_idx += 1
            self._batch_next()

        w.done.connect(on_done)
        w.finished.connect(lambda: self._workers.remove(w) if w in self._workers else None)
        self._workers.append(w)
        w.start()

    # ── Repacking ──────────────────────────────────────────────────────────

    def _repack_dialog(self):
        in_dir = QFileDialog.getExistingDirectory(
            self, "Select Extracted Bundle Folder (must contain manifest.json)", self._out_base
        )
        if not in_dir:
            return

        manifest_path = os.path.join(in_dir, "manifest.json")
        if not os.path.exists(manifest_path):
            QMessageBox.warning(
                self, "Invalid Folder",
                "No manifest.json found.\nSelect a folder created by this tool's extraction."
            )
            return

        default = os.path.basename(in_dir) + "_repacked.bundle"
        fname, ok = QInputDialog.getText(
            self, "Output Filename", "Repacked bundle filename:", text=default
        )
        if not ok or not fname.strip():
            return

        out_path = os.path.join(backend.DEFAULT_REPACK_DIR, fname.strip())
        dlg = OperationDialog("Repacking Bundle", self)
        dlg.append_log(f"Input  : {in_dir}")
        dlg.append_log(f"Output : {out_path}\n")

        w = RepackWorker(in_dir, out_path)
        w.progress.connect(dlg.update_progress)
        w.log.connect(dlg.append_log)
        # pass in_dir as well so sideload knows the original path
        w.done.connect(lambda r: self._on_repack_done(r, dlg, out_path, in_dir))
        w.finished.connect(lambda: self._workers.remove(w) if w in self._workers else None)
        self._workers.append(w)
        w.start()
        dlg.exec()

    def _on_repack_done(self, result: dict, dlg: OperationDialog, out_path: str, in_dir: str):
        """
        in_dir  — the extracted folder (contains manifest.json).
        out_path — the freshly-repacked .bundle file.
        """
        dlg.finish(result["success"])
        if not result["success"]:
            dlg.append_log(f"Error: {result['message']}")
            return

        dlg.append_log(f"Saved to: {out_path}")

        msg = QMessageBox(self)
        msg.setWindowTitle("Repack Complete")
        msg.setText(
            f"Bundle repacked successfully.\n\n"
            f"{os.path.basename(out_path)}\n\n"
            "What would you like to do?"
        )
        msg.setIcon(QMessageBox.Question)

        btn_install = msg.addButton("📲  Install to Game",  QMessageBox.AcceptRole)
        btn_open    = msg.addButton("📁  Open Folder",      QMessageBox.ActionRole)
        msg.addButton("Close",                              QMessageBox.RejectRole)
        msg.exec()

        clicked = msg.clickedButton()
        if clicked == btn_install:
            self._begin_sideload(in_dir, out_path)
        elif clicked == btn_open:
            os.startfile(os.path.dirname(os.path.abspath(out_path)))

    def _begin_sideload(self, in_dir: str, repacked_path: str):
        """
        Deploy the repacked bundle back into the game directory.

        The restore point was already created when the bundle was first extracted,
        so no second compression step is needed.  If the user later hits Undo,
        that snapshot is restored automatically.
        """
        # ── Read original path from manifest ─────────────────────────────────
        manifest_path = os.path.join(in_dir, "manifest.json")
        original_path = ""
        try:
            import json as _json
            with open(manifest_path, "r", encoding="utf-8") as f:
                original_path = _json.load(f).get("original_bundle_path", "")
        except Exception as e:
            QMessageBox.critical(self, "Sideload Error", f"Could not read manifest:\n{e}")
            return

        if not original_path or not os.path.isfile(original_path):
            # Let the user locate it manually
            original_path, _ = QFileDialog.getOpenFileName(
                self,
                "Locate Original Game Bundle",
                backend.JP_BUNDLE_PATH if self._version == "JP" else backend.GL_BUNDLE_PATH,
                "Bundle Files (*.bundle);;All Files (*)",
            )
            if not original_path:
                return

        # ── Confirm ───────────────────────────────────────────────────────────
        # Find matching DB entry so we can mention there's a restore point ready
        entry = _find_snapshot_for(original_path)
        restore_note = (
            f"\n✅ Restore point exists — you can undo this from the Undo/History tab."
            if entry else
            f"\n⚠ No restore point found for this file."
            "\n  Extract the bundle first to create one automatically."
        )

        ans = QMessageBox.question(
            self, "Install to Game",
            f"Copy repacked bundle to game directory?\n\n"
            f"  From : {os.path.basename(repacked_path)}\n"
            f"  To   : {original_path}"
            f"{restore_note}",
            QMessageBox.Yes | QMessageBox.No,
        )
        if ans != QMessageBox.Yes:
            return

        # ── Copy ──────────────────────────────────────────────────────────────
        op_dlg = OperationDialog("Installing Bundle", self)
        op_dlg.append_log(f"Source : {repacked_path}")
        op_dlg.append_log(f"Target : {original_path}\n")

        w = SideloadWorker(original_path, repacked_path)
        w.progress.connect(op_dlg.update_progress)
        w.log.connect(op_dlg.append_log)
        w.done.connect(lambda ok, msg: self._on_sideload_done(ok, msg, op_dlg))
        w.finished.connect(lambda: self._workers.remove(w) if w in self._workers else None)
        self._workers.append(w)
        w.start()
        op_dlg.exec()

    def _on_sideload_done(self, success: bool, message: str, dlg: OperationDialog):
        dlg.finish(success)
        dlg.append_log(f"\n{message}")
        if success:
            self._set_status("✅ Bundle installed — use Undo/History tab to revert.")

    # ── Misc ───────────────────────────────────────────────────────────────

    def _set_status(self, msg: str):
        self._status.setText(msg)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    # High-DPI
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("G.E.M.A.T.R.I.A - Graphical Environment & Modding Architecture for Total Resource Intervention & Analysis")
    app.setStyleSheet(QSS)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()