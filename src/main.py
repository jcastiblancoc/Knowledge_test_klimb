import os
import uuid
from datetime import datetime

from fastapi import FastAPI, Request, Form, HTTPException, status, Response, Cookie
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from models import User, Operation, Bid
from connection import session
from helpers import (
    verify_password,
    create_access_token,
    get_oauth2_scheme,
    get_pwd_context,
    logger,
    get_user_by_email,
    get_user_by_id
)
from auth import authenticate_user
from schemas import (
    LoginForm,
    OperationCreateRequest,
    OperationUpdateRequest,
    BidRequest
)
from seeder import run_seeder

app = FastAPI()

run_seeder()

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory="templates")

oauth2_scheme = get_oauth2_scheme()
pwd_context = get_pwd_context()
logger_info = logger()
SECRET_KEY = os.getenv("SECRET_KEY")


@app.get("/register", response_class=HTMLResponse)
async def show_register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register_user(
    first_name: str = Form(...),
    last_name: str = Form(...),
    nickname: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    country: str = Form(...),
    state: str = Form(...),
    city: str = Form(...)
):
    existing_user = get_user_by_email(email)
    if existing_user:
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")

    new_user = User(
        id=str(uuid.uuid4()),
        first_name=first_name,
        last_name=last_name,
        nickname=nickname,
        email=email,
        phone=phone,
        password=pwd_context.hash(password),
        role=role,
        country=country,
        state=state,
        city=city,
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return RedirectResponse(url="/index", status_code=303)


@app.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="token")
    return {"message": "Sesión cerrada correctamente."}


@app.get("/")
async def redirect_to_index():
    return RedirectResponse(url="/index")


@app.get("/index", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/token")
async def login(form_data: LoginForm, response: Response):
    user = get_user_by_email(form_data.username)

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    response.set_cookie(key="token", value=access_token, httponly=True)

    return {"message": "Logged in successfully", "role": user.role}


@app.get("/users/me")
async def read_users_me(token: str = Cookie(None)):
    return await authenticate_user(token)


@app.get("/operator_dashboard", response_class=HTMLResponse)
async def operator_dashboard(request: Request):
    user = await authenticate_user(request.cookies.get("token"))
    if user.role != "Operator":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso")

    return templates.TemplateResponse("operator_dashboard.html", {"request": request, "user": user})


@app.get("/operator/create-operation", response_class=HTMLResponse)
async def create_operation_page(request: Request):
    return templates.TemplateResponse("create_operation.html", {"request": request})


@app.post("/operator/create-operation")
async def create_operation(operation: OperationCreateRequest, token: str = Cookie(None)):
    user = await authenticate_user(token)

    db_operation = Operation(
        id=str(uuid.uuid4()),
        operator_id=user.id,
        required_amount=operation.required_amount,
        annual_interest=operation.annual_interest,
        deadline=operation.deadline,
        current_amount=operation.current_amount,
    )

    session.add(db_operation)
    session.commit()

    return RedirectResponse(url="create-operation", status_code=303)


@app.get("/operator/operations")
async def list_operations_page(request: Request):
    user = await authenticate_user(request.cookies.get("token"))

    operations = session.query(Operation).all()
    operations_list = [
        {
            'id': operation.id,
            'operator_id': operation.operator_id,
            'annual_interest': float(operation.annual_interest),
            'current_amount': float(operation.current_amount),
            'created_at': operation.created_at.strftime("%d-%m-%Y"),
            'required_amount': float(operation.required_amount),
            'status': operation.status,
            'deadline': operation.deadline.strftime("%d-%m-%Y"),
        }
        for operation in operations
    ]

    return templates.TemplateResponse("operations.html", {"request": request, "operations": operations_list})


@app.put("/operator/update-status")
async def update_status(request: OperationUpdateRequest):
    db_operation = session.query(Operation).filter(Operation.id == request.operation_id).first()

    if not db_operation:
        raise HTTPException(status_code=404, detail="Operation not found")

    db_operation.status = not db_operation.status
    session.commit()

    return JSONResponse(content={"message": "Operación actualizada con éxito."}, status_code=200)


@app.get("/investor_dashboard", response_class=HTMLResponse)
async def investor_dashboard(request: Request):
    user = await authenticate_user(request.cookies.get("token"))
    if user.role != "Investor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso")

    return templates.TemplateResponse("investor_dashboard.html", {"request": request, "user": user})


@app.get("/investor/operations")
async def list_investor_operations_page(request: Request):
    user = await authenticate_user(request.cookies.get("token"))
    operations = session.query(Operation).filter(Operation.status == True).all()

    operations_list = [
        {
            'id': operation.id,
            'operator_id': operation.operator_id,
            'annual_interest': float(operation.annual_interest),
            'current_amount': float(operation.current_amount),
            'created_at': operation.created_at.strftime("%d-%m-%Y"),
            'required_amount': float(operation.required_amount),
            'status': operation.status,
            'deadline': operation.deadline.strftime("%d-%m-%Y"),
        }
        for operation in operations
    ]

    return templates.TemplateResponse("investor_operations.html", {"request": request, "operations": operations_list})


@app.post("/investor/make-offer")
async def make_offer(bid_request: BidRequest, request: Request):
    user = await authenticate_user(request.cookies.get("token"))
    operation = session.query(Operation).filter(Operation.id == bid_request.operation_id).first()

    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")

    new_bid = Bid(
        id=str(uuid.uuid4()),
        investor_id=user.id,
        operation_id=bid_request.operation_id,
        invested_amount=bid_request.invested_amount,
        interest_rate=bid_request.interest_rate,
        bid_date=datetime.now(),
    )

    session.add(new_bid)
    session.commit()

    return {"message": "Oferta enviada exitosamente"}


@app.get("/investor/my-bids")
async def get_user_bids(request: Request):
    user = await authenticate_user(request.cookies.get("token"))

    bids = session.query(Bid).filter(Bid.investor_id == user.id).all()

    return templates.TemplateResponse("my_bids.html", {"request": request, "bids": bids})


@app.get("/admin_dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    user = await authenticate_user(request.cookies.get("token"))
    if user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso")

    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "user": user})


@app.get("/admin/users", response_class=HTMLResponse)
async def list_users(request: Request):
    user = await authenticate_user(request.cookies.get("token"))
    if user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso")

    users = session.query(User).filter(User.id != user.id).all()
    return templates.TemplateResponse("admin_users.html", {"request": request, "users": users})


@app.post("/admin/users/add")
async def add_user(request: Request):
    user_data = await request.json()
    admin_user = await authenticate_user(request.cookies.get("token"))

    if admin_user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso")

    new_user = User(
        id=str(uuid.uuid4()),
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        nickname=user_data["nickname"],
        email=user_data["email"],
        phone=user_data["phone"],
        password=pwd_context.hash(user_data["password"]),
        role=user_data["role"],
        country=user_data["country"],
        state=user_data["state"],
        city=user_data["city"]
    )
    session.add(new_user)
    session.commit()

    return {"message": "Usuario añadido exitosamente", "user_id": new_user.id}


@app.delete("/admin/users/delete/{user_id}")
async def delete_user(user_id: str):
    user = get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    session.delete(user)
    session.commit()

    return {"detail": "Usuario eliminado exitosamente"}
