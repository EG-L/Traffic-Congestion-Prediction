"""
교통 혼잡 예측 모델 학습 스크립트

사용법:
    python train.py              # LightGBM + LSTM 모두 학습
    python train.py --lgbm-only  # LightGBM만 학습
    python train.py --lstm-only  # LSTM만 학습
"""

import os
import pickle
import argparse
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

WEIGHTS_DIR = os.path.join(os.path.dirname(__file__), "app", "models", "weights")
os.makedirs(WEIGHTS_DIR, exist_ok=True)


# ──────────────────────────────────────────────
# 1. 합성 데이터 생성
# ──────────────────────────────────────────────

def generate_data(days: int = 180) -> pd.DataFrame:
    """현실적인 교통 패턴을 반영한 합성 데이터 생성 (기본 6개월)"""
    print(f"[데이터] {days}일치 합성 데이터 생성 중...")
    records = []
    base = datetime(2025, 1, 1)

    for d in range(days):
        dt = base + timedelta(days=d)
        is_weekend = dt.weekday() >= 5

        for h in range(24):
            for m in [0, 30]:
                # 기본 속도 계산 (시간대별 패턴)
                if is_weekend:
                    if 10 <= h <= 18:
                        base_speed = np.random.normal(55, 10)
                    elif 0 <= h <= 5:
                        base_speed = np.random.normal(90, 8)
                    else:
                        base_speed = np.random.normal(70, 10)
                else:
                    # 평일 출퇴근 혼잡
                    if 7 <= h <= 9:
                        base_speed = np.random.normal(28, 8)
                    elif 18 <= h <= 20:
                        base_speed = np.random.normal(25, 8)
                    elif 12 <= h <= 13:
                        base_speed = np.random.normal(45, 8)
                    elif 0 <= h <= 5:
                        base_speed = np.random.normal(95, 5)
                    else:
                        base_speed = np.random.normal(65, 12)

                # 기상 영향
                precipitation = max(0, np.random.exponential(0.3) if np.random.random() < 0.15 else 0)
                temperature = 15 + 12 * np.sin((d - 80) / 365 * 2 * np.pi) + np.random.normal(0, 3)
                wind_speed = max(0, np.random.normal(3, 2))

                if precipitation > 0:
                    base_speed *= max(0.65, 1 - precipitation * 0.06)
                if precipitation > 5:
                    base_speed *= 0.85
                if temperature < 0:
                    base_speed *= 0.9

                speed = float(np.clip(base_speed + np.random.normal(0, 3), 5, 110))

                # 30분 후 속도 (타깃)
                next_h = h if m == 0 else (h + 1) % 24
                if not is_weekend and 7 <= next_h <= 9:
                    next_speed = max(5, speed * np.random.uniform(0.85, 1.05))
                elif not is_weekend and 18 <= next_h <= 20:
                    next_speed = max(5, speed * np.random.uniform(0.85, 1.05))
                else:
                    next_speed = max(5, speed * np.random.uniform(0.92, 1.08))

                records.append({
                    "hour": h,
                    "minute": m,
                    "weekday": dt.weekday(),
                    "is_weekend": int(is_weekend),
                    "month": dt.month,
                    "speed": round(speed, 1),
                    "precipitation": round(precipitation, 2),
                    "temperature": round(temperature, 1),
                    "wind_speed": round(wind_speed, 1),
                    "next_speed": round(next_speed, 1),
                })

    df = pd.DataFrame(records)
    print(f"[데이터] 총 {len(df):,}개 샘플 생성 완료")
    return df


# ──────────────────────────────────────────────
# 2. LightGBM 학습
# ──────────────────────────────────────────────

def train_lgbm(df: pd.DataFrame):
    import lightgbm as lgb
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error

    print("\n[LightGBM] 학습 시작...")

    features = ["hour", "weekday", "is_weekend", "month", "speed", "precipitation", "temperature"]
    X = df[features].values
    y = df["next_speed"].values

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.15, random_state=42)

    model = lgb.LGBMRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        num_leaves=31,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbose=-1,
    )
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        callbacks=[lgb.early_stopping(50, verbose=False), lgb.log_evaluation(100)],
    )

    val_pred = model.predict(X_val)
    mae = mean_absolute_error(y_val, val_pred)
    print(f"[LightGBM] 검증 MAE: {mae:.2f} km/h")

    path = os.path.join(WEIGHTS_DIR, "lgbm_model.pkl")
    with open(path, "wb") as f:
        pickle.dump(model, f)
    print(f"[LightGBM] 저장 완료 → {path}")


# ──────────────────────────────────────────────
# 3. LSTM 학습
# ──────────────────────────────────────────────

def build_sequences(df: pd.DataFrame, seq_len: int = 12):
    """시계열 시퀀스 생성 (seq_len 스텝 → 다음 속도 예측)"""
    from sklearn.preprocessing import MinMaxScaler

    feature_cols = ["speed", "hour", "precipitation", "temperature", "wind_speed"]
    scaler = MinMaxScaler()
    values = scaler.fit_transform(df[feature_cols].values).astype(np.float32)

    target_scaler = MinMaxScaler()
    targets = target_scaler.fit_transform(df[["next_speed"]].values).flatten().astype(np.float32)

    # 스케일러 저장 (예측 시 역변환용)
    with open(os.path.join(WEIGHTS_DIR, "lstm_scaler.pkl"), "wb") as f:
        pickle.dump({"feature": scaler, "target": target_scaler}, f)

    X, y = [], []
    for i in range(seq_len, len(values)):
        X.append(values[i - seq_len:i])
        y.append(targets[i])

    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)


def train_lstm(df: pd.DataFrame):
    try:
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader, TensorDataset
    except ImportError:
        print("\n[LSTM] PyTorch 미설치 — 건너뜁니다.")
        print("       설치: pip install torch")
        return

    from app.models.predictor import LSTMModel

    print("\n[LSTM] 학습 시작...")

    SEQ_LEN = 12
    EPOCHS = 30
    BATCH = 256
    LR = 0.001

    X, y = build_sequences(df, SEQ_LEN)
    split = int(len(X) * 0.85)
    X_train, X_val = X[:split], X[split:]
    y_train, y_val = y[:split], y[split:]

    train_ds = TensorDataset(torch.FloatTensor(X_train), torch.FloatTensor(y_train))
    val_ds = TensorDataset(torch.FloatTensor(X_val), torch.FloatTensor(y_val))
    train_dl = DataLoader(train_ds, batch_size=BATCH, shuffle=True)
    val_dl = DataLoader(val_ds, batch_size=BATCH)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = LSTMModel(input_size=5, hidden_size=64, num_layers=2).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    criterion = nn.MSELoss()
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

    best_val_loss = float("inf")
    best_state = None

    for epoch in range(1, EPOCHS + 1):
        model.train()
        for xb, yb in train_dl:
            xb, yb = xb.to(device), yb.to(device)
            optimizer.zero_grad()
            pred = model(xb).squeeze()
            loss = criterion(pred, yb)
            loss.backward()
            optimizer.step()
        scheduler.step()

        model.eval()
        val_losses = []
        with torch.no_grad():
            for xb, yb in val_dl:
                xb, yb = xb.to(device), yb.to(device)
                pred = model(xb).squeeze()
                val_losses.append(criterion(pred, yb).item())

        val_loss = np.mean(val_losses)
        val_mae = np.mean(np.abs(
            model(torch.FloatTensor(X_val).to(device)).squeeze().cpu().detach().numpy() - y_val
        ))

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

        if epoch % 5 == 0:
            print(f"  Epoch {epoch:2d}/{EPOCHS} | val_loss: {val_loss:.4f} | val_MAE: {val_mae:.2f} km/h")

    path = os.path.join(WEIGHTS_DIR, "lstm_model.pth")
    torch.save(best_state, path)
    print(f"[LSTM] 저장 완료 → {path}")


# ──────────────────────────────────────────────
# 4. 메인
# ──────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lgbm-only", action="store_true")
    parser.add_argument("--lstm-only", action="store_true")
    parser.add_argument("--days", type=int, default=180, help="합성 데이터 생성 일수")
    args = parser.parse_args()

    start = datetime.now()
    df = generate_data(days=args.days)

    if not args.lstm_only:
        train_lgbm(df)

    if not args.lgbm_only:
        train_lstm(df)

    elapsed = (datetime.now() - start).seconds
    print(f"\n[완료] 학습 완료 ({elapsed}초) - weights/ 폴더를 확인하세요.")
