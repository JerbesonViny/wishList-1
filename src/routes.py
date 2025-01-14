from pydantic.types import Json
from pydantic import BaseModel
from fastapi import status, Header
from typing import Optional, Dict, List
import json

from src import app
from src.database.schemas import *
from src.headers import create_token, decode_token
from src.controllers.usercontroller import UserController
from src.controllers.authcontroller import UserProfileController
from src.controllers.productcontroller import ProductController
from src.controllers.wishlistcontroller import WishListController

class UserModel(BaseModel):
  name: Optional[str]
  nickname: Optional[str]
  email: Optional[str]
  password: Optional[str]

class ProductModel(BaseModel):
  title: str
  desc: Optional[str]
  uri: Optional[str]
  img: Optional[str]
  status: Optional[str]

@app.get('/')
def home():
  return {'msg': "Hello world"}

# User Routes

@app.get('/list-users/')
def list_users():
  controller = UserController()

  return controller.index()

@app.post('/register/')
def create_user(user: UserModel):
  if( user ):
    controller = UserController()

    return controller.create(user)

  return {'msg': 'Body is required!'}

@app.post('/login/')
def login(data: dict):
  userProfile = UserProfileController()
  result = userProfile.auth_login(data)

  if( not result ):
    return {'msg': 'Invalid login'}

  return create_token(result)

@app.post('/logout/')
def logout(token: Optional[str] = Header(None)):
  if( decode_token(token) == None):
    return {'msg': 'token is required'}

  return {'token': None}

@app.put("/update-user/{user_id}")
def update_user(user_id:int, user: UserModel, token: Optional[str] = Header(None)):
  token_decoded = decode_token(token)

  if( token_decoded == None):
    return {'msg': 'token is required'}

  if( user ):

    controller = UserController()

    return controller.update(token_decoded['id'], user)

  return {'msg': 'Body is required!'}

@app.delete('/delete-user/{user_id}')
def delete_user(password: UserModel, token: Optional[str] = Header(None)):
  token_decoded = decode_token(token)

  if( token_decoded == None):
    return {'msg': 'token is required'}

  if( not password ):
    return json.dumps({'msg': 'body is required'})

  controller = UserController()
  return controller.delete(password, token_decoded['id'])

#Product Routes

@app.get('/list-products/')
def list_products():
  controller = ProductController()

  return controller.index()

@app.post('/create-product/')
def create_product(data: List[ProductModel], token: Optional[str] = Header(None)):
  token_decoded = decode_token(token)
  if( token_decoded == None ):
    return {'msg': 'token is required'}

  controller = ProductController()
  product_list = controller.create(data, token_decoded['id'])

  wishcontroller = WishListController()
  wishcontroller.create(product_list, token_decoded['id'])

  return product_list

@app.post('/update-product')
def update_product(products: List[ProductModel], token: Optional[str] = Header(None)):
  token_decoded = decode_token(token)
  if ( token_decoded == None ):
    return {'msg': 'token is required'}

  controller = ProductController()
  id_product = controller.search_by_body(products[0], token_decoded['id'])

  return controller.update(products[1], token_decoded['id'], id_product[0])

@app.delete('/delete-product')
def delete_product(product, token: Optional[str] = Header(None)):
  token_decoded = decode_token(token)
  if( token_decoded == None ):
      return {'msg': 'token is required'}

  if( not product ):
    return json.dumps({'msg': 'body is required'})

  controller = ProductController()

  return controller.delete(product, token_decoded['id'])

# WishList Routes

@app.get('/wishlist/')
def get_wishlist(username: Optional[str] = None, token: Optional[str] = Header(None)):
  token_decoded = decode_token(token)
  controller = WishListController()
  if( token_decoded == None ):
    return {'msg': 'token is required'}

  if( not username ):
    username = token_decoded['nickname']

  return controller.search_by_username(username)

@app.post('/have-product')
def status_update(product: ProductModel, status, token: Optional[str] = Header(None)):
  return {'product': product, 'status': status}

@app.get('/wishlist/random')
def random_list(token: Optional[str] = Header(None)):
  token_decoded = decode_token(token)

  if( token_decoded == None ):
    return {'msg': 'token is required'}
  controller = WishListController()

  return controller.random(token_decoded['id'])

@app.get('/wishlist/owned')
def owned_products(token: Optional[str] = Header(None)):
  token_decoded = decode_token(token)

  if( token_decoded == None ):
     return {'msg': 'token is required'}

  controller = ProductController()

  return controller.get_products_owned(token_decoded['id'])

@app.post('/wishlist/favorite-item/{product_id}')
def favorite_item(product_id: Optional[int], token: Optional[str] = Header(None)):
  token_decoded = decode_token(token)

  if( token_decoded == None ):
     return {'msg': 'token is required'}

  controller = WishListController()

  return controller.favorite_item(product_id, token_decoded['id'])
