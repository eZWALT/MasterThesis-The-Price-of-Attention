"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          RECOMMENDER SYSTEMS — Hello World & Model Comparison               ║
║          Covering: CF · Content-Based · Neural · Sequential · LLM-hybrid    ║
╚══════════════════════════════════════════════════════════════════════════════╝

RECSYS TAXONOMY (Bird's Eye View)
══════════════════════════════════

┌─────────────────────────────────────────────────────────────┐
│                  RECOMMENDER SYSTEMS                        │
├──────────────────┬──────────────────┬───────────────────────┤
│  COLLABORATIVE   │  CONTENT-BASED   │       HYBRID          │
│   FILTERING      │   FILTERING      │                       │
├──────────────────┴──────────────────┴───────────────────────┤
│ CF                                                          │
│  ├─ Memory-Based                                            │
│  │   ├─ User-User KNN                                       │
│  │   └─ Item-Item KNN                                       │
│  └─ Model-Based                                             │
│      ├─ Matrix Factorization (SVD, NMF, PMF)               │
│      ├─ Factorization Machines (FM, FFM)                    │
│      ├─ ALS (iALS, wALS)                                    │
│      ├─ BPR (Bayesian Personalized Ranking)                 │
│      └─ Deep Learning CF                                    │
│          ├─ NCF (NeuMF)  [He et al. 2017]                  │
│          ├─ AutoRec      [Sedhain et al. 2015]              │
│          └─ LightGCN     [He et al. 2020]                  │
│                                                             │
│ CONTENT-BASED                                               │
│  ├─ TF-IDF / BM25 profiles                                 │
│  └─ Deep features (BERT, CNNs)                              │
│                                                             │
│ SEQUENTIAL / SESSION-BASED                                  │
│  ├─ GRU4Rec     [Hidasi et al. 2015]                       │
│  ├─ SASRec      [Kang & McAuley 2018]                      │
│  ├─ BERT4Rec    [Sun et al. 2019]                           │
│  └─ SSE-PT      [Wu et al. 2020]                            │
│                                                             │
│ KNOWLEDGE-AWARE                                             │
│  ├─ RippleNet, KGCN, KGAT                                  │
│  └─ KGNN-LS                                                 │
│                                                             │
│ LLM / CONVERSATIONAL (FRONTIER)                             │
│  ├─ P5           [Geng et al. 2022]  — prompt-based        │
│  ├─ InstructRec  [Zhang et al. 2023]                        │
│  ├─ LLMRank      [Hou et al. 2023]                          │
│  ├─ RAG-based    retrieve → re-rank via LLM                 │
│  └─ Conversational RecSys (CRS)                             │
│      ├─ KBQAN, UNICORN, UniCRS                              │
│      └─ GPT4Rec / OpenP5                                    │
│                                                             │
│ METRICS                                                     │
│  ├─ Accuracy: HR@K, NDCG@K, MRR, Precision, Recall, AUC   │
│  ├─ Beyond-accuracy: Coverage, Diversity, Serendipity       │
│  └─ Business: CTR, CVR, RPM, Retention (DAU/MAU)           │
└─────────────────────────────────────────────────────────────┘

INSTALL (run once):
    pip install pandas numpy scipy scikit-learn scikit-surprise \
                implicit torch tqdm requests rich colorama

DATA SOURCES:
    - MovieLens 1M / 25M   → auto-downloaded here
    - Amazon Reviews 2023  → https://amazon-reviews-2023.github.io/
    - Yelp Dataset         → https://www.yelp.com/dataset
    - RecSys Challenge     → https://recsys.acm.org/challenges/
    - MIND (News)          → https://msnews.github.io/
    - Tenrec (Tencent)     → https://github.com/yuangh-x/2022-NIPS-Tenrec
    - KuaiRec              → https://kuairec.com/
"""

# ─────────────────────────────────────────────────────────────────────────────
# 0. IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
import os, sys, time, warnings, zipfile, urllib.request, random
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity

# Rich terminal output (optional but nice)
try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import track
    from rich import print as rprint
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None

warnings.filterwarnings("ignore")
np.random.seed(42)
random.seed(42)

# ─────────────────────────────────────────────────────────────────────────────
# 1. DATA DOWNLOAD & LOADING
# ─────────────────────────────────────────────────────────────────────────────

DATA_DIR = Path("./recsys_data")
DATA_DIR.mkdir(exist_ok=True)


def download_movielens_1m() -> pd.DataFrame:
    """Download MovieLens 1M (1M ratings, 6K users, 4K movies)."""
    url = "https://files.grouplens.org/datasets/movielens/ml-1m.zip"
    zip_path = DATA_DIR / "ml-1m.zip"
    data_path = DATA_DIR / "ml-1m" / "ratings.dat"

    if not data_path.exists():
        print("⬇  Downloading MovieLens 1M …")
        urllib.request.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(DATA_DIR)
        print("✓  MovieLens 1M downloaded")

    ratings = pd.read_csv(
        data_path, sep="::", engine="python",
        names=["user_id", "item_id", "rating", "timestamp"]
    )
    # Also load movie metadata
    movies_path = DATA_DIR / "ml-1m" / "movies.dat"
    movies = pd.read_csv(
        movies_path, sep="::", engine="python",
        names=["item_id", "title", "genres"], encoding="latin-1"
    )
    print(f"   Ratings: {len(ratings):,} | Users: {ratings.user_id.nunique():,} | Items: {ratings.item_id.nunique():,}")
    return ratings, movies


def download_movielens_100k() -> pd.DataFrame:
    """Download MovieLens 100K (lightweight, fast for prototyping)."""
    url = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"
    zip_path = DATA_DIR / "ml-100k.zip"
    data_path = DATA_DIR / "ml-100k" / "u.data"

    if not data_path.exists():
        print("⬇  Downloading MovieLens 100K …")
        urllib.request.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(DATA_DIR)
        print("✓  MovieLens 100K downloaded")

    ratings = pd.read_csv(
        data_path, sep="\t",
        names=["user_id", "item_id", "rating", "timestamp"]
    )
    print(f"   Ratings: {len(ratings):,} | Users: {ratings.user_id.nunique()} | Items: {ratings.item_id.nunique()}")
    return ratings


def get_amazon_sample_url(category: str = "Movies_and_TV") -> str:
    """
    Amazon Reviews 2023 — McAuley Lab (UCSD).
    Full datasets at: https://amazon-reviews-2023.github.io/
    Small 5-core subsets available per category.
    Categories: 'Books', 'Electronics', 'Movies_and_TV', 'Video_Games', etc.
    """
    base = "https://datarepo.eng.ucsd.edu/mcauley_group/data/amazon_2023/benchmark/5core/rating_only"
    return f"{base}/{category}.csv.gz"


# ─────────────────────────────────────────────────────────────────────────────
# 2. DATA PREPROCESSING
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class RecDataset:
    """Standardized dataset container for all RecSys models."""
    name: str
    train: pd.DataFrame
    val: pd.DataFrame
    test: pd.DataFrame
    n_users: int
    n_items: int
    user_enc: LabelEncoder
    item_enc: LabelEncoder
    # For implicit feedback
    train_matrix: Optional[csr_matrix] = None
    # item_id → list of user_ids (for leave-one-out eval)
    ground_truth: Dict[int, List[int]] = field(default_factory=dict)


def binarize_ratings(df: pd.DataFrame, threshold: float = 3.5) -> pd.DataFrame:
    """Convert explicit ratings to implicit feedback (clicked / not clicked)."""
    df = df.copy()
    df["label"] = (df["rating"] >= threshold).astype(int)
    return df[df["label"] == 1].drop(columns=["label"])


def leave_one_out_split(df: pd.DataFrame, seed: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Leave-One-Out split: most recent item → test, second most recent → val.
    Standard protocol for sequential RecSys evaluation.
    """
    df = df.sort_values(["user_id", "timestamp"])
    df["rank"] = df.groupby("user_id").cumcount(ascending=False)
    test  = df[df["rank"] == 0].drop(columns=["rank"])
    val   = df[df["rank"] == 1].drop(columns=["rank"])
    train = df[df["rank"] >  1].drop(columns=["rank"])
    return train, val, test


def build_dataset(ratings: pd.DataFrame, dataset_name: str = "MovieLens",
                  implicit: bool = True) -> RecDataset:
    """Full preprocessing pipeline → RecDataset."""
    if implicit:
        ratings = binarize_ratings(ratings)

    # Re-encode IDs to 0-indexed integers
    ue, ie = LabelEncoder(), LabelEncoder()
    ratings = ratings.copy()
    ratings["user_id"] = ue.fit_transform(ratings["user_id"])
    ratings["item_id"] = ie.fit_transform(ratings["item_id"])

    # Filter users with < 5 interactions (cold-start pruning)
    counts = ratings.groupby("user_id").size()
    keep   = counts[counts >= 5].index
    ratings = ratings[ratings["user_id"].isin(keep)]

    train, val, test = leave_one_out_split(ratings)

    n_users = ratings["user_id"].nunique()
    n_items = ratings["item_id"].nunique()

    # Build sparse interaction matrix (users × items)
    rows = train["user_id"].values
    cols = train["item_id"].values
    data = np.ones(len(rows))
    mat  = csr_matrix((data, (rows, cols)), shape=(n_users, n_items))

    # Ground truth for evaluation {user_id: [test_item_id]}
    gt = test.groupby("user_id")["item_id"].apply(list).to_dict()

    return RecDataset(
        name=dataset_name, train=train, val=val, test=test,
        n_users=n_users, n_items=n_items,
        user_enc=ue, item_enc=ie,
        train_matrix=mat, ground_truth=gt,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 3. EVALUATION METRICS
# ─────────────────────────────────────────────────────────────────────────────

def hit_rate_at_k(recommended: List[int], relevant: List[int], k: int) -> float:
    """HR@K — did any relevant item appear in top-K?"""
    return float(len(set(recommended[:k]) & set(relevant)) > 0)


def ndcg_at_k(recommended: List[int], relevant: List[int], k: int) -> float:
    """NDCG@K — normalised discounted cumulative gain."""
    relevant_set = set(relevant)
    dcg = sum(
        1.0 / np.log2(i + 2)
        for i, item in enumerate(recommended[:k])
        if item in relevant_set
    )
    idcg = sum(1.0 / np.log2(i + 2) for i in range(min(len(relevant), k)))
    return dcg / idcg if idcg > 0 else 0.0


def mrr_at_k(recommended: List[int], relevant: List[int], k: int) -> float:
    """MRR@K — mean reciprocal rank."""
    relevant_set = set(relevant)
    for i, item in enumerate(recommended[:k]):
        if item in relevant_set:
            return 1.0 / (i + 1)
    return 0.0


def precision_at_k(recommended: List[int], relevant: List[int], k: int) -> float:
    return len(set(recommended[:k]) & set(relevant)) / k


def recall_at_k(recommended: List[int], relevant: List[int], k: int) -> float:
    if not relevant:
        return 0.0
    return len(set(recommended[:k]) & set(relevant)) / len(relevant)


def catalog_coverage(all_recommendations: List[List[int]], n_items: int) -> float:
    """% of catalog ever recommended (diversity proxy)."""
    recommended_items = set(item for recs in all_recommendations for item in recs)
    return len(recommended_items) / n_items


def evaluate_model(
    model_fn,           # callable: user_id → sorted list of recommended item_ids
    dataset: RecDataset,
    k: int = 10,
    n_eval_users: int = 500,
    neg_sample_size: int = 99,   # 99 negatives + 1 positive → 100-way ranking
) -> Dict[str, float]:
    """
    Standard evaluation protocol: 100-way negative sampling.
    For each test user: rank 1 positive + 99 random negatives.
    Reports HR@K, NDCG@K, MRR@K, Precision@K, Recall@K.
    """
    train_items_per_user = (
        dataset.train.groupby("user_id")["item_id"].apply(set).to_dict()
    )
    all_items = set(range(dataset.n_items))

    metrics = defaultdict(list)
    all_top_k = []

    eval_users = list(dataset.ground_truth.keys())
    random.shuffle(eval_users)
    eval_users = eval_users[:n_eval_users]

    for uid in eval_users:
        pos_items = dataset.ground_truth[uid]
        seen      = train_items_per_user.get(uid, set())
        # Sample negatives
        candidates = list(all_items - seen - set(pos_items))
        negs = random.sample(candidates, min(neg_sample_size, len(candidates)))
        pool = pos_items + negs

        # Score pool
        scores = model_fn(uid, pool)  # {item_id: score}
        ranked = sorted(pool, key=lambda x: scores.get(x, 0.0), reverse=True)

        metrics["hr"].append(hit_rate_at_k(ranked, pos_items, k))
        metrics["ndcg"].append(ndcg_at_k(ranked, pos_items, k))
        metrics["mrr"].append(mrr_at_k(ranked, pos_items, k))
        metrics["precision"].append(precision_at_k(ranked, pos_items, k))
        metrics["recall"].append(recall_at_k(ranked, pos_items, k))
        all_top_k.append(ranked[:k])

    results = {m: float(np.mean(v)) for m, v in metrics.items()}
    results["coverage"] = catalog_coverage(all_top_k, dataset.n_items)
    return results


# ─────────────────────────────────────────────────────────────────────────────
# 4. BASELINE MODELS
# ─────────────────────────────────────────────────────────────────────────────

class RandomRecommender:
    """Random baseline — lower bound."""
    def __init__(self, n_items: int):
        self.n_items = n_items

    def fit(self, dataset: RecDataset): pass

    def score(self, user_id: int, item_ids: List[int]) -> Dict[int, float]:
        return {i: random.random() for i in item_ids}


class PopularityRecommender:
    """
    Popularity baseline — recommend most interacted items.
    Strong baseline; often hard to beat in aggregate metrics.
    Maps directly to 'trending' / 'bestseller' ad strategies.
    """
    def __init__(self): self.item_scores = {}

    def fit(self, dataset: RecDataset):
        counts = dataset.train["item_id"].value_counts()
        self.item_scores = counts.to_dict()

    def score(self, user_id: int, item_ids: List[int]) -> Dict[int, float]:
        return {i: self.item_scores.get(i, 0) for i in item_ids}


# ─────────────────────────────────────────────────────────────────────────────
# 5. MEMORY-BASED COLLABORATIVE FILTERING
# ─────────────────────────────────────────────────────────────────────────────

class ItemKNNRecommender:
    """
    Item-Item Collaborative Filtering.
    Classic: Sarwar et al. (2001), Amazon item-to-item (Linden et al. 2003).
    Intuition: users who liked X also liked Y → recommend Y to new users of X.
    """
    def __init__(self, k: int = 50):
        self.k = k
        self.item_sim: Optional[np.ndarray] = None
        self.user_item_matrix: Optional[csr_matrix] = None

    def fit(self, dataset: RecDataset):
        mat = dataset.train_matrix  # users × items
        # Item similarity: cosine on item-user vectors
        item_mat = mat.T.toarray().astype(np.float32)
        norms = np.linalg.norm(item_mat, axis=1, keepdims=True) + 1e-9
        item_mat_norm = item_mat / norms
        self.item_sim = item_mat_norm @ item_mat_norm.T  # items × items
        self.user_item_matrix = mat
        print(f"  ItemKNN fitted | sim matrix: {self.item_sim.shape}")

    def score(self, user_id: int, item_ids: List[int]) -> Dict[int, float]:
        if user_id >= self.user_item_matrix.shape[0]:
            return {i: 0.0 for i in item_ids}
        user_vec = self.user_item_matrix[user_id].toarray().flatten()
        interacted = np.where(user_vec > 0)[0]
        scores = {}
        for iid in item_ids:
            if len(interacted) == 0 or iid >= len(self.item_sim):
                scores[iid] = 0.0
            else:
                sim_scores = self.item_sim[iid, interacted]
                top_k_sim  = np.sort(sim_scores)[-self.k:]
                scores[iid] = float(top_k_sim.mean())
        return scores


# ─────────────────────────────────────────────────────────────────────────────
# 6. MATRIX FACTORIZATION — SVD / PMF
# ─────────────────────────────────────────────────────────────────────────────

class SVDRecommender:
    """
    Truncated SVD / Simon Funk SVD (Netflix Prize winner).
    Equivalent to latent factor model:  R ≈ U · Σ · Vᵀ
    References: Koren et al. "Matrix Factorization Techniques" (2009).
    """
    def __init__(self, n_factors: int = 64, n_epochs: int = 20,
                 lr: float = 0.005, reg: float = 0.02):
        self.n_factors = n_factors
        self.n_epochs  = n_epochs
        self.lr        = lr
        self.reg       = reg

    def fit(self, dataset: RecDataset):
        n_u, n_i = dataset.n_users, dataset.n_items
        self.P = np.random.normal(0, 0.1, (n_u, self.n_factors))  # users
        self.Q = np.random.normal(0, 0.1, (n_i, self.n_factors))  # items
        self.bu = np.zeros(n_u)   # user biases
        self.bi = np.zeros(n_i)   # item biases
        self.mu = dataset.train.get("rating", pd.Series(np.ones(len(dataset.train)))).mean()

        data = dataset.train[["user_id", "item_id"]].copy()
        data["r"] = 1.0  # implicit

        print(f"  SVD training {self.n_epochs} epochs …")
        for epoch in range(self.n_epochs):
            df = data.sample(frac=1)  # shuffle
            total_loss = 0.0
            for row in df.itertuples(index=False):
                u, i, r = int(row.user_id), int(row.item_id), float(row.r)
                pred = self.mu + self.bu[u] + self.bi[i] + self.P[u] @ self.Q[i]
                e    = r - pred
                self.bu[u] += self.lr * (e - self.reg * self.bu[u])
                self.bi[i] += self.lr * (e - self.reg * self.bi[i])
                self.P[u]  += self.lr * (e * self.Q[i] - self.reg * self.P[u])
                self.Q[i]  += self.lr * (e * self.P[u] - self.reg * self.Q[i])
                total_loss += e ** 2
            if (epoch + 1) % 5 == 0:
                print(f"    Epoch {epoch+1}/{self.n_epochs}  MSE={total_loss/len(df):.4f}")

    def score(self, user_id: int, item_ids: List[int]) -> Dict[int, float]:
        if user_id >= len(self.P):
            return {i: 0.0 for i in item_ids}
        valid = [i for i in item_ids if i < len(self.Q)]
        preds = self.P[user_id] @ self.Q[valid].T
        scores = {i: float(p) for i, p in zip(valid, preds)}
        for i in item_ids:
            if i not in scores:
                scores[i] = 0.0
        return scores


# ─────────────────────────────────────────────────────────────────────────────
# 7. ALS / BPR via `implicit` library (fast C++ backend)
# ─────────────────────────────────────────────────────────────────────────────

class ALSRecommender:
    """
    Alternating Least Squares for implicit feedback.
    Hu, Koren & Volinsky (2008) — scales to millions of users.
    Used in production at Spotify, Netflix, etc.
    """
    def __init__(self, factors: int = 64, iterations: int = 15,
                 regularization: float = 0.01):
        self.factors        = factors
        self.iterations     = iterations
        self.regularization = regularization
        self.model          = None

    def fit(self, dataset: RecDataset):
        try:
            import implicit
            self.model = implicit.als.AlternatingLeastSquares(
                factors=self.factors,
                iterations=self.iterations,
                regularization=self.regularization,
                random_state=42,
            )
            # implicit expects items × users
            mat = dataset.train_matrix.T.astype(np.float32)
            self.model.fit(mat, show_progress=False)
            self._user_factors = self.model.user_factors
            self._item_factors = self.model.item_factors
            print(f"  ALS fitted | factors={self.factors}")
        except ImportError:
            print("  ⚠  `implicit` not installed → using random scores for ALS")
            self._user_factors = None

    def score(self, user_id: int, item_ids: List[int]) -> Dict[int, float]:
        if self._user_factors is None or user_id >= len(self._user_factors):
            return {i: random.random() for i in item_ids}
        u_vec   = self._user_factors[user_id]
        valid   = [i for i in item_ids if i < len(self._item_factors)]
        i_vecs  = self._item_factors[valid]
        preds   = i_vecs @ u_vec
        scores  = {i: float(p) for i, p in zip(valid, preds)}
        for i in item_ids:
            if i not in scores:
                scores[i] = 0.0
        return scores


class BPRRecommender:
    """
    Bayesian Personalised Ranking — Rendle et al. (2009).
    Directly optimises the ranking AUC with pairwise loss:
        BPR-OPT = Σ ln σ(x_ui - x_uj)  [pos item u > neg item j]
    Better for implicit feedback than point-wise MSE.
    """
    def __init__(self, factors: int = 64, iterations: int = 100,
                 learning_rate: float = 0.01, regularization: float = 0.01):
        self.factors        = factors
        self.iterations     = iterations
        self.learning_rate  = learning_rate
        self.regularization = regularization
        self.model          = None

    def fit(self, dataset: RecDataset):
        try:
            import implicit
            self.model = implicit.bpr.BayesianPersonalizedRanking(
                factors=self.factors,
                iterations=self.iterations,
                learning_rate=self.learning_rate,
                regularization=self.regularization,
                random_state=42,
            )
            mat = dataset.train_matrix.T.astype(np.float32)
            self.model.fit(mat, show_progress=False)
            self._user_factors = self.model.user_factors
            self._item_factors = self.model.item_factors
            print(f"  BPR fitted | factors={self.factors}")
        except ImportError:
            print("  ⚠  `implicit` not installed → using random scores for BPR")
            self._user_factors = None

    def score(self, user_id: int, item_ids: List[int]) -> Dict[int, float]:
        if self._user_factors is None or user_id >= len(self._user_factors):
            return {i: random.random() for i in item_ids}
        u_vec  = self._user_factors[user_id]
        valid  = [i for i in item_ids if i < len(self._item_factors)]
        preds  = self._item_factors[valid] @ u_vec
        scores = {i: float(p) for i, p in zip(valid, preds)}
        for i in item_ids:
            if i not in scores:
                scores[i] = 0.0
        return scores


# ─────────────────────────────────────────────────────────────────────────────
# 8. NEURAL COLLABORATIVE FILTERING (NCF / NeuMF)
# ─────────────────────────────────────────────────────────────────────────────

class NeuMF:
    """
    Neural Matrix Factorisation — He et al. (2017).
    Combines GMF (dot product) + MLP in a two-tower architecture:

        GMF branch:  e_u ⊙ e_i
        MLP branch:  MLP([e_u || e_i])
        NeuMF:       h^T · [GMF_output || MLP_output]

    Training: BPR or binary cross-entropy with negative sampling.
    """
    def __init__(self, n_users: int, n_items: int,
                 mf_dim: int = 32, mlp_dims: List[int] = None,
                 dropout: float = 0.2, lr: float = 1e-3,
                 n_epochs: int = 10, batch_size: int = 1024,
                 n_neg: int = 4):
        self.n_users    = n_users
        self.n_items    = n_items
        self.mf_dim     = mf_dim
        self.mlp_dims   = mlp_dims or [64, 32, 16]
        self.dropout    = dropout
        self.lr         = lr
        self.n_epochs   = n_epochs
        self.batch_size = batch_size
        self.n_neg      = n_neg
        self.model      = None

    def _build_model(self):
        try:
            import torch, torch.nn as nn
        except ImportError:
            return None

        class _NeuMF(nn.Module):
            def __init__(s, n_users, n_items, mf_dim, mlp_dims, dropout):
                super().__init__()
                # GMF embeddings
                s.mf_user = nn.Embedding(n_users, mf_dim)
                s.mf_item = nn.Embedding(n_items, mf_dim)
                # MLP embeddings
                mlp_input = mlp_dims[0] * 2
                s.mlp_user = nn.Embedding(n_users, mlp_dims[0])
                s.mlp_item = nn.Embedding(n_items, mlp_dims[0])
                # MLP layers
                layers = []
                in_dim = mlp_input
                for out_dim in mlp_dims[1:]:
                    layers += [nn.Linear(in_dim, out_dim), nn.ReLU(), nn.Dropout(dropout)]
                    in_dim = out_dim
                s.mlp = nn.Sequential(*layers)
                s.output = nn.Linear(mf_dim + mlp_dims[-1], 1)
                # Init
                nn.init.normal_(s.mf_user.weight, std=0.01)
                nn.init.normal_(s.mf_item.weight, std=0.01)
                nn.init.normal_(s.mlp_user.weight, std=0.01)
                nn.init.normal_(s.mlp_item.weight, std=0.01)

            def forward(s, users, items):
                gmf = s.mf_user(users) * s.mf_item(items)
                mlp_in = torch.cat([s.mlp_user(users), s.mlp_item(items)], dim=-1)
                mlp_out = s.mlp(mlp_in)
                x = torch.cat([gmf, mlp_out], dim=-1)
                return s.output(x).squeeze(-1)

        return _NeuMF(self.n_users, self.n_items, self.mf_dim, self.mlp_dims, self.dropout)

    def fit(self, dataset: RecDataset):
        try:
            import torch, torch.nn as nn
        except ImportError:
            print("  ⚠  PyTorch not installed → NCF unavailable")
            return

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.device = device
        self.model  = self._build_model().to(device)
        optimizer   = torch.optim.Adam(self.model.parameters(), lr=self.lr)
        criterion   = nn.BCEWithLogitsLoss()

        # Build positive pairs
        pos_u = dataset.train["user_id"].values
        pos_i = dataset.train["item_id"].values
        n_items = dataset.n_items

        print(f"  NeuMF training on {device} | {self.n_epochs} epochs …")
        self.model.train()
        for epoch in range(self.n_epochs):
            idx   = np.random.permutation(len(pos_u))
            epoch_loss = 0.0; n_batches = 0
            for start in range(0, len(idx), self.batch_size):
                batch_idx = idx[start:start + self.batch_size]
                bu = pos_u[batch_idx]; bi = pos_i[batch_idx]
                # Negative sampling
                neg_i = np.random.randint(0, n_items, size=len(bu) * self.n_neg)
                bu_rep = np.tile(bu, self.n_neg)
                users = np.concatenate([bu, bu_rep])
                items = np.concatenate([bi, neg_i])
                labels = np.concatenate([np.ones(len(bu)), np.zeros(len(neg_i))])
                # Tensors
                t_u = torch.LongTensor(users).to(device)
                t_i = torch.LongTensor(items).to(device)
                t_l = torch.FloatTensor(labels).to(device)
                optimizer.zero_grad()
                logits = self.model(t_u, t_i)
                loss   = criterion(logits, t_l)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item(); n_batches += 1
            if (epoch + 1) % 2 == 0:
                print(f"    Epoch {epoch+1}/{self.n_epochs}  loss={epoch_loss/n_batches:.4f}")
        self.model.eval()

    def score(self, user_id: int, item_ids: List[int]) -> Dict[int, float]:
        if self.model is None:
            return {i: 0.0 for i in item_ids}
        import torch
        with torch.no_grad():
            u = torch.LongTensor([user_id] * len(item_ids)).to(self.device)
            i = torch.LongTensor(item_ids).to(self.device)
            preds = torch.sigmoid(self.model(u, i)).cpu().numpy()
        return {iid: float(p) for iid, p in zip(item_ids, preds)}


# ─────────────────────────────────────────────────────────────────────────────
# 9. LIGHTWEIGHT SEQUENTIAL MODEL (GRU-based)
# ─────────────────────────────────────────────────────────────────────────────

class GRU4RecRecommender:
    """
    Session-based RS using GRU — Hidasi et al. (2015).
    Models user interaction sequences: [i1, i2, i3] → predict i4.
    Key for:  ads retargeting, streaming, e-commerce session CTR.
    SOTA extensions: SASRec (self-attention), BERT4Rec (bidirectional).
    """
    def __init__(self, n_items: int, emb_dim: int = 64,
                 hidden_dim: int = 128, n_layers: int = 1,
                 lr: float = 1e-3, n_epochs: int = 5,
                 batch_size: int = 256, max_seq_len: int = 50):
        self.n_items     = n_items
        self.emb_dim     = emb_dim
        self.hidden_dim  = hidden_dim
        self.n_layers    = n_layers
        self.lr          = lr
        self.n_epochs    = n_epochs
        self.batch_size  = batch_size
        self.max_seq_len = max_seq_len
        self.model       = None
        self._user_seqs: Dict[int, List[int]] = {}

    def _build_sequences(self, dataset: RecDataset):
        df = dataset.train.sort_values(["user_id", "timestamp"])
        self._user_seqs = (
            df.groupby("user_id")["item_id"]
              .apply(list)
              .to_dict()
        )

    def fit(self, dataset: RecDataset):
        try:
            import torch, torch.nn as nn
        except ImportError:
            print("  ⚠  PyTorch not installed → GRU4Rec unavailable")
            return

        self._build_sequences(dataset)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.device = device

        class _GRU4Rec(nn.Module):
            def __init__(s, n_items, emb_dim, hidden_dim, n_layers, dropout=0.2):
                super().__init__()
                s.emb = nn.Embedding(n_items + 1, emb_dim, padding_idx=0)
                s.gru = nn.GRU(emb_dim, hidden_dim, n_layers,
                               batch_first=True, dropout=dropout if n_layers > 1 else 0)
                s.fc  = nn.Linear(hidden_dim, n_items)
            def forward(s, x):
                e = s.emb(x)
                out, _ = s.gru(e)
                return s.fc(out[:, -1, :])  # last hidden state → item logits

        self.model = _GRU4Rec(self.n_items, self.emb_dim,
                               self.hidden_dim, self.n_layers).to(device)
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)
        criterion = nn.CrossEntropyLoss(ignore_index=0)

        # Build (seq, target) pairs
        seqs, targets = [], []
        for uid, seq in self._user_seqs.items():
            seq = [s + 1 for s in seq]  # +1 for padding offset
            for j in range(1, len(seq)):
                s_in = seq[max(0, j - self.max_seq_len):j]
                seqs.append(s_in)
                targets.append(seq[j] - 1)

        print(f"  GRU4Rec training on {device} | {self.n_epochs} epochs …")
        self.model.train()
        for epoch in range(self.n_epochs):
            idx = np.random.permutation(len(seqs))
            epoch_loss = 0.0; n_batches = 0
            for start in range(0, len(idx), self.batch_size):
                batch_idx = idx[start:start + self.batch_size]
                batch_seqs = [seqs[i] for i in batch_idx]
                batch_tgts = [targets[i] for i in batch_idx]
                # Pad sequences
                max_len = max(len(s) for s in batch_seqs)
                padded  = [[0] * (max_len - len(s)) + s for s in batch_seqs]
                t_x = torch.LongTensor(padded).to(device)
                t_y = torch.LongTensor(batch_tgts).to(device)
                optimizer.zero_grad()
                logits = self.model(t_x)
                loss = criterion(logits, t_y)
                loss.backward()
                nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()
                epoch_loss += loss.item(); n_batches += 1
            print(f"    Epoch {epoch+1}/{self.n_epochs}  loss={epoch_loss/n_batches:.4f}")
        self.model.eval()

    def score(self, user_id: int, item_ids: List[int]) -> Dict[int, float]:
        if self.model is None or user_id not in self._user_seqs:
            return {i: 0.0 for i in item_ids}
        import torch
        seq = self._user_seqs[user_id]
        seq_in = [s + 1 for s in seq[-self.max_seq_len:]]
        t_x = torch.LongTensor([seq_in]).to(self.device)
        with torch.no_grad():
            logits = self.model(t_x)[0]  # (n_items,)
            probs  = torch.softmax(logits, dim=-1).cpu().numpy()
        return {iid: float(probs[iid]) if iid < len(probs) else 0.0
                for iid in item_ids}


# ─────────────────────────────────────────────────────────────────────────────
# 10. LLM-HYBRID RECOMMENDER (RAG pattern — pluggable)
# ─────────────────────────────────────────────────────────────────────────────

class LLMRerankRecommender:
    """
    RAG-style LLM Recommender (stub / demonstration).

    Architecture:
        1. RETRIEVAL  — fast CF/BM25 retrieves top-N candidates
        2. RERANKING  — LLM scores/reranks via zero-shot or few-shot prompt
        3. (Optional) EXPLANATION — LLM generates natural-language justification

    Connects to your conversational RecSys research goal:
        ┌──────────────────────────────────────────────────────────┐
        │ User says: "I want something like Inception but lighter" │
        │                                                          │
        │ 1. Parse intent → extract: [genre=sci-fi, mood=light]   │
        │ 2. CF retrieval → top-50 candidates                      │
        │ 3. LLM rerank   → consider conversational context        │
        │ 4. Response      → "Here's Coherence, here's why…"       │
        └──────────────────────────────────────────────────────────┘

    For advertising strategies:
        - Native ads: LLM frames sponsored items naturally in context
        - Exploration: ε-greedy or Thompson sampling at rerank stage
        - Diversity: MMR (Maximal Marginal Relevance) post-processing

    References:
        - LLMRank: Hou et al. (2023) "Large Language Models are Zero-Shot Rankers"
        - InstructRec: Zhang et al. (2023)
        - P5: Geng et al. (2022) "Recommendation as Language Processing"
        - RAGRec: Deldjoo et al. (2024)
    """
    def __init__(self, base_recommender, item_metadata: Dict[int, str] = None,
                 llm_fn=None, n_candidates: int = 50):
        """
        base_recommender : any fitted RecSys model with .score()
        item_metadata    : {item_id: "title + description"} for LLM context
        llm_fn           : callable(prompt: str) → str  (OpenAI/Anthropic/local)
        """
        self.base   = base_recommender
        self.meta   = item_metadata or {}
        self.llm    = llm_fn
        self.n_cand = n_candidates

    def fit(self, dataset: RecDataset):
        pass  # base model should already be fitted

    def score(self, user_id: int, item_ids: List[int],
              user_query: str = "") -> Dict[int, float]:
        """
        Without LLM: falls back to base model.
        With LLM:    reranks top-N using zero-shot prompt scoring.
        """
        base_scores = self.base.score(user_id, item_ids)

        if self.llm is None:
            return base_scores  # graceful degradation

        # Get top-N candidates from base model
        ranked_items  = sorted(item_ids, key=lambda x: base_scores[x], reverse=True)
        candidates    = ranked_items[:self.n_cand]

        # Build rerank prompt
        item_list = "\n".join(
            f"{idx+1}. {self.meta.get(iid, f'Item {iid}')}"
            for idx, iid in enumerate(candidates)
        )
        prompt = f"""
        You are a recommendation engine. The user said: "{user_query}"
        Rerank these {len(candidates)} items by relevance (most relevant first).
        Return ONLY a JSON list of item indices (1-indexed), e.g.: [3, 1, 7, ...]

        Items:
        {item_list}
        """
        try:
            response = self.llm(prompt)
            import json, re
            ranks = json.loads(re.search(r"\[.*\]", response, re.S).group())
            scores = {candidates[r-1]: float(len(ranks) - i)
                      for i, r in enumerate(ranks) if 0 < r <= len(candidates)}
            # Fall back to base scores for non-reranked items
            for iid in item_ids:
                if iid not in scores:
                    scores[iid] = base_scores[iid]
            return scores
        except Exception:
            return base_scores


def make_openai_llm(api_key: str, model: str = "gpt-4o-mini"):
    """Factory for OpenAI-backed LLM function (plug into LLMRerankRecommender)."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        def llm_fn(prompt: str) -> str:
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            return r.choices[0].message.content
        return llm_fn
    except ImportError:
        print("pip install openai to use OpenAI LLM reranking")
        return None


def make_anthropic_llm(api_key: str, model: str = "claude-haiku-4-5-20251001"):
    """Factory for Anthropic-backed LLM function."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        def llm_fn(prompt: str) -> str:
            r = client.messages.create(
                model=model, max_tokens=512,
                messages=[{"role": "user", "content": prompt}]
            )
            return r.content[0].text
        return llm_fn
    except ImportError:
        print("pip install anthropic to use Claude LLM reranking")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# 11. EXPERIMENT RUNNER
# ─────────────────────────────────────────────────────────────────────────────

def print_results_table(results: Dict[str, Dict[str, float]], k: int = 10):
    """Print a comparison table of all models."""
    metric_cols = ["hr", "ndcg", "mrr", "precision", "recall", "coverage"]
    header = f"\n{'Model':<25}" + "".join(f"{m.upper()+'@'+str(k):>12}" for m in metric_cols[:-1]) + f"{'COVERAGE':>12}"
    print("=" * (25 + 12 * len(metric_cols)))
    print(header)
    print("-" * (25 + 12 * len(metric_cols)))
    for model_name, metrics in sorted(results.items(), key=lambda x: -x[1].get("ndcg", 0)):
        row = f"{model_name:<25}"
        for m in metric_cols:
            v = metrics.get(m, 0.0)
            row += f"{v:>12.4f}"
        print(row)
    print("=" * (25 + 12 * len(metric_cols)))


def run_experiment(
    use_dataset: str = "ml-100k",   # "ml-100k" or "ml-1m"
    k: int = 10,
    n_eval_users: int = 300,
    run_neural: bool = True,
    run_sequential: bool = True,
):
    """
    Full experiment pipeline:
      1. Download data
      2. Preprocess
      3. Fit all models
      4. Evaluate
      5. Print comparison table
    """
    print("\n" + "═" * 65)
    print("  RECSYS BENCHMARK SUITE")
    print(f"  Dataset: {use_dataset} | K={k} | eval_users={n_eval_users}")
    print("═" * 65 + "\n")

    # ── Data ──────────────────────────────────────────────────────────
    t0 = time.time()
    if use_dataset == "ml-1m":
        ratings, movies = download_movielens_1m()
        meta = dict(zip(movies.item_id, movies.title))
    else:
        ratings = download_movielens_100k()
        meta = {}

    dataset = build_dataset(ratings, dataset_name=use_dataset)
    print(f"\n  Dataset built in {time.time()-t0:.1f}s")
    print(f"  Train={len(dataset.train):,}  Val={len(dataset.val):,}  Test={len(dataset.test):,}")
    print(f"  Users={dataset.n_users:,}  Items={dataset.n_items:,}\n")

    # Re-encode meta keys
    if meta and hasattr(dataset.item_enc, "classes_"):
        le = dataset.item_enc
        meta_encoded = {}
        for orig_id, title in meta.items():
            if orig_id in le.classes_:
                enc_id = le.transform([orig_id])[0]
                meta_encoded[enc_id] = title
        meta = meta_encoded

    # ── Models ────────────────────────────────────────────────────────
    models = {
        "Random":     RandomRecommender(dataset.n_items),
        "Popularity": PopularityRecommender(),
        "ItemKNN":    ItemKNNRecommender(k=50),
        "SVD":        SVDRecommender(n_factors=64, n_epochs=15),
        "ALS":        ALSRecommender(factors=64, iterations=20),
        "BPR":        BPRRecommender(factors=64, iterations=100),
    }

    if run_neural:
        models["NeuMF"] = NeuMF(
            n_users=dataset.n_users, n_items=dataset.n_items,
            mf_dim=32, mlp_dims=[64, 32, 16], n_epochs=8,
        )

    if run_sequential:
        models["GRU4Rec"] = GRU4RecRecommender(
            n_items=dataset.n_items, emb_dim=64,
            hidden_dim=128, n_epochs=5,
        )

    # ── Train & Evaluate ──────────────────────────────────────────────
    results = {}
    for name, model in models.items():
        print(f"\n[{name}] fitting …")
        t_fit = time.time()
        model.fit(dataset)
        fit_time = time.time() - t_fit

        print(f"[{name}] evaluating …")
        t_eval = time.time()
        score_fn = model.score  # compatible signature: (user_id, item_ids) → dict
        metrics  = evaluate_model(score_fn, dataset, k=k, n_eval_users=n_eval_users)
        eval_time = time.time() - t_eval

        metrics["fit_time"]  = fit_time
        metrics["eval_time"] = eval_time
        results[name]        = metrics
        print(f"  HR@{k}={metrics['hr']:.4f}  NDCG@{k}={metrics['ndcg']:.4f}  "
              f"MRR@{k}={metrics['mrr']:.4f}  (fit={fit_time:.1f}s)")

    # ── Results ───────────────────────────────────────────────────────
    print_results_table(results, k=k)

    # ── Timing summary ─────────────────────────────────────────────
    print("\n  TRAINING TIME SUMMARY")
    print(f"  {'Model':<25} {'Fit (s)':>10} {'Eval (s)':>10}")
    print("  " + "-" * 45)
    for name, m in results.items():
        print(f"  {name:<25} {m['fit_time']:>10.1f} {m['eval_time']:>10.1f}")

    return results, dataset


# ─────────────────────────────────────────────────────────────────────────────
# 12. ADVERTISING STRATEGY STUBS
# ─────────────────────────────────────────────────────────────────────────────
"""
ADVERTISING STRATEGIES FOR CONVERSATIONAL RECSYS
══════════════════════════════════════════════════

The space where RecSys meets ads optimisation:

┌─────────────────────────────────────────────────────────────────────────┐
│  STRATEGY          │ OPTIMISES      │ RISK             │ LLM HOOK       │
├────────────────────┼────────────────┼──────────────────┼────────────────┤
│ Pure Exploitation  │ CTR            │ Filter bubble    │ System prompt  │
│  (greedy recs)     │                │ User churn       │ "rank by CTR"  │
├────────────────────┼────────────────┼──────────────────┼────────────────┤
│ ε-Greedy Explore   │ CTR + coverage │ Worse short-term │ Occasionally   │
│                    │                │ CTR              │ inject random  │
├────────────────────┼────────────────┼──────────────────┼────────────────┤
│ Thompson Sampling  │ Long-term CTR  │ Complex to tune  │ Bayesian       │
│ (Bandit)           │ + retention    │                  │ uncertainty    │
├────────────────────┼────────────────┼──────────────────┼────────────────┤
│ Native Ads (LLM)   │ CTR + UX       │ Trust erosion    │ "mention X     │
│                    │                │ if disclosed     │ naturally"     │
├────────────────────┼────────────────┼──────────────────┼────────────────┤
│ Diversity          │ Retention +    │ Lower CTR        │ MMR reranking  │
│ (MMR / DPP)        │ satisfaction   │                  │ in prompt      │
├────────────────────┼────────────────┼──────────────────┼────────────────┤
│ Serendipity        │ Long-term NPS  │ Lower short-term │ "surprise me"  │
│ injection          │                │ metrics          │ intent parsing │
└────────────────────┴────────────────┴──────────────────┴────────────────┘
"""

def epsilon_greedy_rerank(scores: Dict[int, float], epsilon: float = 0.1) -> Dict[int, float]:
    """
    ε-greedy exploration: with prob ε replace top-K with random items.
    Trades short-term CTR for long-term coverage & retention.
    """
    if random.random() < epsilon:
        # exploration: shuffle scores slightly
        items = list(scores.keys())
        random.shuffle(items)
        return {item: float(len(items) - i) for i, item in enumerate(items)}
    return scores


def mmr_rerank(scores: Dict[int, float], item_embeddings: np.ndarray,
               lambda_: float = 0.5, k: int = 10) -> List[int]:
    """
    Maximal Marginal Relevance — Carbonell & Goldstein (1998).
    Balances relevance (CTR proxy) vs diversity:
        MMR = λ · relevance(i) - (1-λ) · max_j∈S sim(i, j)
    """
    items = list(scores.keys())
    if not items or item_embeddings is None:
        return sorted(items, key=lambda x: scores[x], reverse=True)[:k]

    selected = []
    candidates = items.copy()

    for _ in range(min(k, len(candidates))):
        if not selected:
            best = max(candidates, key=lambda x: scores[x])
        else:
            sel_embs = item_embeddings[selected]
            best, best_score = None, -np.inf
            for c in candidates:
                if c >= len(item_embeddings):
                    continue
                rel  = scores[c]
                sim  = cosine_similarity(item_embeddings[c:c+1], sel_embs).max()
                mmr  = lambda_ * rel - (1 - lambda_) * sim
                if mmr > best_score:
                    best_score = mmr; best = c
            if best is None:
                break
        selected.append(best)
        candidates.remove(best)

    return selected


class ThompsonSamplingBandit:
    """
    Thompson Sampling for item recommendation.
    Models CTR per item as Beta distribution: Beta(α, β).
    Each interaction updates α (successes) or β (failures).
    Naturally balances exploration vs exploitation.
    Great for ad slot optimisation alongside CF recall.
    """
    def __init__(self, n_items: int):
        self.alpha = np.ones(n_items)   # successes (clicks)
        self.beta  = np.ones(n_items)   # failures (non-clicks)

    def sample_scores(self, item_ids: List[int]) -> Dict[int, float]:
        scores = {}
        for i in item_ids:
            if i < len(self.alpha):
                scores[i] = float(np.random.beta(self.alpha[i], self.beta[i]))
            else:
                scores[i] = float(np.random.beta(1, 1))
        return scores

    def update(self, item_id: int, clicked: bool):
        if item_id < len(self.alpha):
            if clicked:
                self.alpha[item_id] += 1
            else:
                self.beta[item_id]  += 1


# ─────────────────────────────────────────────────────────────────────────────
# 13. ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="RecSys Hello World")
    parser.add_argument("--dataset",     default="ml-100k",
                        choices=["ml-100k", "ml-1m"],
                        help="Dataset to use (100k is faster for prototyping)")
    parser.add_argument("--k",           type=int, default=10,
                        help="Recommendation list length for evaluation")
    parser.add_argument("--eval-users",  type=int, default=300,
                        help="Number of users for evaluation sampling")
    parser.add_argument("--no-neural",   action="store_true",
                        help="Skip PyTorch models (NCF, GRU4Rec)")
    parser.add_argument("--no-seq",      action="store_true",
                        help="Skip sequential model (GRU4Rec)")
    args = parser.parse_args()

    results, dataset = run_experiment(
        use_dataset    = args.dataset,
        k              = args.k,
        n_eval_users   = args.eval_users,
        run_neural     = not args.no_neural,
        run_sequential = not args.no_seq and not args.no_neural,
    )

    print("\n\n  NEXT STEPS FOR YOUR RESEARCH")
    print("  " + "─" * 50)
    print("""
  1. CONVERSATIONAL RECSYS
     ├─ Add intent parsing (spaCy / LLM) to extract preferences
     ├─ Plug LLMRerankRecommender with make_anthropic_llm()
     └─ Track multi-turn context with a ConversationMemory dict

  2. AD STRATEGY EXPERIMENTS
     ├─ Wrap score() with epsilon_greedy_rerank(ε=0.05..0.3)
     ├─ Replace with ThompsonSamplingBandit for online learning
     └─ Measure CTR/Retention tradeoff with A/B simulation

  3. AMAZON DATA (richer item metadata)
     ├─ url = get_amazon_sample_url("Video_Games")
     ├─ df  = pd.read_csv(url, compression="gzip")
     └─ Pass to build_dataset() — same pipeline works

  4. SCALE UP
     ├─ LightGCN  → pip install torch-geometric
     ├─ SASRec    → github.com/kang205/SASRec
     ├─ BERT4Rec  → github.com/FeiSun/BERT4Rec
     └─ RecBole   → recbole.io  (unified benchmark framework)

  5. LLM RERANKING (production pattern)
     llm = make_anthropic_llm(api_key="sk-ant-...")
     ranker = LLMRerankRecommender(base_model, meta, llm)
     ranked = ranker.score(uid, candidates, user_query="sci-fi")
  """)
