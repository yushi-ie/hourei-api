import os
from uuid import uuid4
import boto3
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File

load_dotenv()

# S3 Setup
S3_BUCKET_NAME = settings.S3_BUCKET_NAME
if not S3_BUCKET_NAME:
    # Fallback to env var if not in settings, though settings should handle it
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    if not S3_BUCKET_NAME:
         raise RuntimeError("S3_BUCKET_NAME is not set in .env or config")

s3_client = boto3.client("s3")

router = APIRouter(prefix="/auth", tags=["auth"])


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(models.User).filter(models.User.username == username).first()


@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # すでに同じユーザー名が登録されていないかチェック
    user = get_user_by_username(db, user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # パスワードをハッシュ化
    hashed_password = get_password_hash(user_in.password)

    # 新しいユーザーを作成してDBに保存
    new_user = models.User(
        username=user_in.username,
        hashed_password=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/token")
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = get_user_by_username(db, form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(
        data={"sub": str(user.id)}  # user.id を JWT に入れる
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me")
def read_users_me(
    current_user: Annotated[models.User, Depends(get_current_active_user)],
):
    return {
        "id": current_user.id,
        "username": current_user.username,
    }

@router.post("/users/me/photos")
async def upload_my_photo(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
):
    if file.content_type is None or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="画像ファイルをアップロードしてください。",
        )

    # S3 に保存するキー（パス）を作成
    ext = os.path.splitext(file.filename)[1] or ""
    key = f"users/{current_user.id}/{uuid4().hex}{ext}"

    # ファイル内容を読み込んで S3 にアップロード
    content = await file.read()
    s3_client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=key,
        Body=content,
        ContentType=file.content_type,
    )

    # 簡易的な公開URL（バケットをそのまま公開にはしていない前提）
    url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{key}"

    return {
        "key": key,
        "url": url,
        "filename": file.filename,
        "content_type": file.content_type,
    }

@router.post("/users", response_model=User)
async def create_user(user: User, password: str):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="User already registered")
    
    fake_users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "disabled": user.disabled,
        "hashed_password": get_password_hash(password)
    }
    return user
