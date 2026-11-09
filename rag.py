
import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

KNOWLEDGE_FILE = (
    BASE_DIR / "knowledge" / "disease_knowledge.json"
)

DB_DIR = BASE_DIR / "knowledge" / "chroma_db"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

COLLECTION_NAME = "crop_guardian_knowledge"

TOP_K = 3


# ==========================================
# 2. INITIALIZE DATABASE
# ==========================================

client = chromadb.PersistentClient(
    path=str(DB_DIR)
)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)


# ==========================================
# 3. LOAD EMBEDDING MODEL
# ==========================================

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)

print("Embedding model loaded successfully.")


# ==========================================
# 4. LOAD KNOWLEDGE
# ==========================================

def load_knowledge():

    if not KNOWLEDGE_FILE.exists():
        raise FileNotFoundError(KNOWLEDGE_FILE)

    with open(
        KNOWLEDGE_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(
            "Knowledge JSON must contain a list."
        )

    return data


# ==========================================
# 5. NORMALIZE DISEASE NAMES
# ==========================================

def normalize_name(value):

    return (
        str(value)
        .lower()
        .replace("_", " ")
        .strip()
    )


# ==========================================
# 6. PREPARE DOCUMENT TEXT
# ==========================================

def prepare_document(entry):

    sections = [
        f"Crop: {entry['crop']}",
        f"Disease: {entry['disease']}",

        f"Scientific name: "
        f"{entry.get('scientific_name', '')}",

        "Symptoms: "
        + "; ".join(entry.get("symptoms", [])),

        "Early signs: "
        + "; ".join(entry.get("early_signs", [])),

        "Low-cost actions: "
        + "; ".join(entry.get("low_cost_actions", [])),

        "Chemical options: "
        + "; ".join(entry.get("chemical_options", [])),

        "Favorable conditions: "
        + "; ".join(entry.get("favorable_conditions", []))
    ]

    return "\n".join(sections)


# ==========================================
# 7. BUILD VECTOR DATABASE
# ==========================================

def build_database():

    entries = load_knowledge()

    if not entries:
        raise ValueError(
            "Knowledge base is empty."
        )

    documents = []
    embeddings = []
    ids = []
    metadatas = []

    for entry in entries:

        required = [
            "id",
            "crop",
            "disease",
            "source_name",
            "source_url"
        ]

        missing = [
            field
            for field in required
            if not entry.get(field)
        ]

        if missing:
            raise ValueError(
                f"Entry {entry.get('id')} missing: {missing}"
            )

        document = prepare_document(entry)

        embedding = embedding_model.encode(
            document,
            normalize_embeddings=True
        ).tolist()

        documents.append(document)
        embeddings.append(embedding)
        ids.append(entry["id"])

        metadatas.append({
            "crop": entry["crop"].lower(),
            "disease": entry["disease"],
            "source_name": entry["source_name"],
            "source_url": entry["source_url"],
            "verification_status": entry.get(
                "verification_status",
                "unverified"
            )
        })

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print("\nDATABASE BUILT SUCCESSFULLY")
    print("Knowledge entries:", len(entries))
    print("Database location:", DB_DIR)

    return len(entries)


# ==========================================
# 8. SEARCH KNOWLEDGE
# ==========================================

def search(
    crop: str,
    disease: str,
    top_k: int = TOP_K
):

    crop = str(crop).lower().strip()
    disease = normalize_name(disease)

    if not crop or not disease:
        raise ValueError(
            "Crop and disease are required."
        )

    if top_k < 1:
        raise ValueError(
            "top_k must be at least 1."
        )

    # --------------------------------------
    # A. Check that database is available
    # --------------------------------------

    if collection.count() == 0:

        raise RuntimeError(
            "Knowledge database is empty. "
            "Run build_database() first."
        )

    # --------------------------------------
    # B. Check exact disease name in JSON
    # --------------------------------------

    entries = load_knowledge()

    matching_entries = [
        entry
        for entry in entries

        if entry["crop"].lower().strip() == crop

        and normalize_name(
            entry["disease"]
        ) == disease
    ]

    # --------------------------------------
    # C. Reject unknown disease
    # --------------------------------------

    if not matching_entries:

        return {
            "status": "no_reliable_match",
            "crop": crop,
            "query": disease,
            "matches": [],
            "message": (
                "No verified knowledge entry exists "
                "for this crop and disease."
            )
        }

    # --------------------------------------
    # D. Retrieve matching disease knowledge
    # --------------------------------------

    exact_disease = matching_entries[0]["disease"]

    query = (
        f"Crop: {crop}. "
        f"Disease: {exact_disease}. "
        "Find symptoms, early signs and "
        "management advice."
    )

    query_embedding = embedding_model.encode(
        query,
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],

        n_results=min(
            top_k,
            collection.count()
        ),

        where={
    "$and": [
        {"crop": {"$eq": crop}},
        {"disease": {"$eq": exact_disease}}
    ]
},

        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    # --------------------------------------
    # E. Format retrieved results
    # --------------------------------------

    matches = []

    for i in range(len(results["ids"][0])):

        metadata = results["metadatas"][0][i]

        matches.append({

            "id": results["ids"][0][i],

            "document": results["documents"][0][i],

            "disease": metadata["disease"],

            "source_name": metadata["source_name"],

            "source_url": metadata["source_url"],

            "verification_status": metadata[
                "verification_status"
            ],

            "distance": round(
                results["distances"][0][i],
                4
            )
        })

    # --------------------------------------
    # F. Return structured response
    # --------------------------------------

    if not matches:

        return {
            "status": "no_reliable_match",
            "crop": crop,
            "query": disease,
            "matches": [],
            "message": (
                "No matching knowledge was found "
                "in the vector database."
            )
        }

    return {
        "status": "success",
        "crop": crop,
        "query": disease,
        "matches": matches,
        "message": "Matching knowledge retrieved."
    }


# ==========================================
# 9. TERMINAL TEST
# ==========================================

if __name__ == "__main__":

    import sys

    if len(sys.argv) < 3:

        print(
            'Usage: python rag.py <crop> "<disease>"'
        )

        print(
            'Example: python rag.py potato "Late blight"'
        )

        raise SystemExit(1)

    crop = sys.argv[1]
    disease = sys.argv[2]

    # Build database if empty
    if collection.count() == 0:

        build_database()

    # Search knowledge
    result = search(crop, disease)

    print("\n========== RAG SEARCH RESULTS ==========")

    print("Status:", result["status"])
    print("Crop:", result["crop"])
    print("Query:", result["query"])

    if result["status"] == "success":

        for item in result["matches"]:

            print("\nDisease:", item["disease"])

            print("Source:", item["source_name"])

            print(
                "Verification:",
                item["verification_status"]
            )

            print("Distance:", item["distance"])

            print("Information:")
            print(item["document"])

            print("Source URL:", item["source_url"])

    else:

        print("\n", result["message"])

    print("\n========================================")
