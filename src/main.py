import os
from fastapi import FastAPI, Request, Form, HTTPException, status, Response, Cookie
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models import User, Operation, Bid
from connection import session
from helpers import verify_password, create_access_token, get_oauth2_scheme, get_pwd_context, logger, get_current_user
import uuid
from schemas import LoginForm, OperationCreateRequest, OperationUpdateRequest


app = FastAPI()


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
    existing_user = session.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")

    user_data = {
        "id": str(uuid.uuid4()),
        "first_name": first_name,
        "last_name": last_name,
        "nickname": nickname,
        "email": email,
        "phone": phone,
        "password": pwd_context.hash(password),
        "role": role,
        "country": country,
        "state": state,
        "city": city
    }

    new_user = User(**user_data)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return RedirectResponse(url="/login", status_code=303)

@app.get("/index", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/token")
async def login(form_data: LoginForm, response: Response):
    user = session.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email, "role": user.role})

    response.set_cookie(key="token", value=access_token, httponly=True)
    logger_info.info(f"Token establecido: {access_token}")
    return {"message": "Logged in successfully", "role": user.role}

@app.get("/users/me")
async def read_users_me(token: str = Cookie(None)):
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        user = get_current_user(token)
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@app.get("/operator_dashboard", response_class=HTMLResponse)
async def operator_dashboard(request: Request):
    token = request.cookies.get("token")
    if not token:
        return {"detail": "No estás autenticado"}, 401
    user = get_current_user(token)
    if user.role != "Operator":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso")

    return templates.TemplateResponse("operator_dashboard.html", {"request": request, "user": user})


@app.get("/investor_dashboard", response_class=HTMLResponse)
async def investor_dashboard(request: Request):
    token = request.cookies.get("token")
    if not token:
        return {"detail": "No estás autenticado"}, 401
    user = get_current_user(token)
    if user.role != "Investor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso")
    
    return templates.TemplateResponse("investor_dashboard.html", {"request": request, "user": user})


@app.get("/admin_dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    token = request.cookies.get("token")
    if not token:
        return {"detail": "No estás autenticado"}, 401
    user = get_current_user(token)
    user = await read_users_me(token)
    if user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso")
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "user": user})


@app.get("/operator/create-operation", response_class=HTMLResponse)
async def create_operation_page(request: Request):
    return templates.TemplateResponse("create_operation.html", {"request": request})
@app.get("/operator/create-operation", response_class=HTMLResponse)


@app.post("/operator/create-operation")
async def create_operation(
    operation: OperationCreateRequest,
    token: str = Cookie(None)
):
    user = await read_users_me(token)
    db_operation = Operation(
        id=str(uuid.uuid4()),
        operator_id=user.id,
        required_amount=operation.required_amount,
        annual_interest=operation.annual_interest,
        deadline=operation.deadline,
        current_amount=operation.current_amount
    )
    session.add(db_operation)
    session.commit()

    return RedirectResponse(url="create-operation", status_code=303)

@app.get("/operator/operations")
async def list_operations_page(request: Request):
    user = await read_users_me(request.cookies.get("token"))
    if not user:
        return {"detail": "No estás autenticado"}, 401
    operations = session.query(Operation).all()

    operations_list = []
    for operation in operations:
        data = {
            'id': operation.id,
            'operator_id': operation.operator_id,
            'annual_interest': float(operation.annual_interest),
            'current_amount': float(operation.current_amount),
            'created_at': (operation.created_at).strftime("%d-%m-%Y"),
            'required_amount': float(operation.required_amount),
            'status': operation.status,
            'deadline': (operation.deadline).strftime("%d-%m-%Y")
        }
        operations_list.append(data)

    return templates.TemplateResponse("operations.html", {"request": request, "operations": operations_list})


@app.put("/operator/update-status")
async def update_status(request: OperationUpdateRequest):
    db_operation = session.query(Operation).where(Operation.id == request.operation_id).first()

    if not db_operation:
        raise HTTPException(status_code=404, detail="Operation not found")

    db_operation.status = not db_operation.status
    session.commit()

    return JSONResponse(content={"message": "Operación actualizada con éxito."}, status_code=200)
