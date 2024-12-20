def serialize_document(doc):
    """Convert MongoDB document ObjectId to string for JSON."""
    doc["_id"] = str(doc["_id"])
    return doc

def serialize_documents(documents):
    return [serialize_document(doc) for doc in documents]
