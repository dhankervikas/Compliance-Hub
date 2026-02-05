import React from 'react';
import {
    Bold,
    Italic,
    Underline,
    Strikethrough,
    AlignLeft,
    AlignCenter,
    AlignRight,
    AlignJustify,
    List,
    ListOrdered,
    Heading1,
    Heading2,
    Heading3,
    Undo,
    Redo,
    Table as TableIcon,
    Trash2,
    Columns,
    Rows
} from 'lucide-react';

const EditorToolbar = ({ editor }) => {
    if (!editor) {
        return null;
    }

    const ToolbarButton = ({ onClick, isActive, disabled, children, title }) => (
        <button
            onClick={onClick}
            disabled={disabled}
            title={title}
            className={`p-2 rounded-lg transition-colors ${isActive
                ? 'bg-purple-100 text-purple-700'
                : 'text-gray-600 hover:bg-gray-100 placeholder-gray-400'
                } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
            {children}
        </button>
    );

    const Divider = () => <div className="w-px h-6 bg-gray-200 mx-1 self-center" />;

    return (
        <div className="border border-gray-200 bg-white rounded-lg shadow-sm p-2 mb-4 flex flex-wrap gap-1 sticky top-0 z-10 w-full max-w-[210mm] mx-auto">
            {/* History */}
            <div className="flex gap-1">
                <ToolbarButton onClick={() => editor.chain().focus().undo().run()} disabled={!editor.can().undo()} title="Undo">
                    <Undo className="w-4 h-4" />
                </ToolbarButton>
                <ToolbarButton onClick={() => editor.chain().focus().redo().run()} disabled={!editor.can().redo()} title="Redo">
                    <Redo className="w-4 h-4" />
                </ToolbarButton>
            </div>

            <Divider />

            {/* Headings */}
            <div className="flex gap-1">
                <ToolbarButton
                    onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
                    isActive={editor.isActive('heading', { level: 1 })}
                    title="Heading 1"
                >
                    <Heading1 className="w-4 h-4" />
                </ToolbarButton>
                <ToolbarButton
                    onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
                    isActive={editor.isActive('heading', { level: 2 })}
                    title="Heading 2"
                >
                    <Heading2 className="w-4 h-4" />
                </ToolbarButton>
                <ToolbarButton
                    onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
                    isActive={editor.isActive('heading', { level: 3 })}
                    title="Heading 3"
                >
                    <Heading3 className="w-4 h-4" />
                </ToolbarButton>
            </div>

            <Divider />

            {/* Formatting */}
            <div className="flex gap-1">
                <ToolbarButton
                    onClick={() => editor.chain().focus().toggleBold().run()}
                    isActive={editor.isActive('bold')}
                    title="Bold"
                >
                    <Bold className="w-4 h-4" />
                </ToolbarButton>
                <ToolbarButton
                    onClick={() => editor.chain().focus().toggleItalic().run()}
                    isActive={editor.isActive('italic')}
                    title="Italic"
                >
                    <Italic className="w-4 h-4" />
                </ToolbarButton>
                <ToolbarButton
                    onClick={() => editor.chain().focus().toggleUnderline().run()}
                    isActive={editor.isActive('underline')}
                    title="Underline"
                >
                    <Underline className="w-4 h-4" />
                </ToolbarButton>
                <ToolbarButton
                    onClick={() => editor.chain().focus().toggleStrike().run()}
                    isActive={editor.isActive('strike')}
                    title="Strikethrough"
                >
                    <Strikethrough className="w-4 h-4" />
                </ToolbarButton>
            </div>

            <Divider />

            {/* Lists */}
            <div className="flex gap-1">
                <ToolbarButton
                    onClick={() => editor.chain().focus().toggleBulletList().run()}
                    isActive={editor.isActive('bulletList')}
                    title="Bullet List"
                >
                    <List className="w-4 h-4" />
                </ToolbarButton>
                <ToolbarButton
                    onClick={() => editor.chain().focus().toggleOrderedList().run()}
                    isActive={editor.isActive('orderedList')}
                    title="Ordered List"
                >
                    <ListOrdered className="w-4 h-4" />
                </ToolbarButton>
            </div>

            <Divider />

            {/* Alignment */}
            <div className="flex gap-1">
                <ToolbarButton
                    onClick={() => editor.chain().focus().setTextAlign('left').run()}
                    isActive={editor.isActive({ textAlign: 'left' })}
                    title="Align Left"
                >
                    <AlignLeft className="w-4 h-4" />
                </ToolbarButton>
                <ToolbarButton
                    onClick={() => editor.chain().focus().setTextAlign('center').run()}
                    isActive={editor.isActive({ textAlign: 'center' })}
                    title="Align Center"
                >
                    <AlignCenter className="w-4 h-4" />
                </ToolbarButton>
                <ToolbarButton
                    onClick={() => editor.chain().focus().setTextAlign('right').run()}
                    isActive={editor.isActive({ textAlign: 'right' })}
                    title="Align Right"
                >
                    <AlignRight className="w-4 h-4" />
                </ToolbarButton>
                <ToolbarButton
                    onClick={() => editor.chain().focus().setTextAlign('justify').run()}
                    isActive={editor.isActive({ textAlign: 'justify' })}
                    title="Justify"
                >
                    <AlignJustify className="w-4 h-4" />
                </ToolbarButton>
            </div>

            <Divider />

            {/* Table Controls */}
            <div className="flex gap-1">
                <ToolbarButton
                    onClick={() => editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()}
                    title="Insert Table"
                >
                    <TableIcon className="w-4 h-4" />
                </ToolbarButton>
                {editor.isActive('table') && (
                    <>
                        <ToolbarButton onClick={() => editor.chain().focus().addColumnAfter().run()} title="Add Column">
                            <Columns className="w-4 h-4" />
                        </ToolbarButton>
                        <ToolbarButton onClick={() => editor.chain().focus().deleteColumn().run()} title="Delete Column" className="text-red-500">
                            <Trash2 className="w-4 h-4 text-red-500" />
                        </ToolbarButton>
                        <ToolbarButton onClick={() => editor.chain().focus().addRowAfter().run()} title="Add Row">
                            <Rows className="w-4 h-4" />
                        </ToolbarButton>
                        <ToolbarButton onClick={() => editor.chain().focus().deleteRow().run()} title="Delete Row" className="text-red-500">
                            <Trash2 className="w-4 h-4 text-red-500" />
                        </ToolbarButton>
                    </>
                )}
            </div>

        </div>
    );
};

export default EditorToolbar;
