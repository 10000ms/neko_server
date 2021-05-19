from handler import note


note_handler = {
    '/note': note.note_index,
    '/note/add': note.note_add,
    '/note/edit': note.note_edit,
    '/note/delete': note.note_delete,
}
