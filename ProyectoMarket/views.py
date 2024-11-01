from django.shortcuts import render,redirect
from django.db import connection
from ProyectoMarket.models import Proveedor,Productos
from django.core.files.storage import FileSystemStorage
from django.core.serializers import serialize #para serializar diccionarios en json
from django.http import HttpResponse # para enviar respuesta directas sin usar un template
import json #para leer y convertir json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout

'''def home(request):
    if request.user.is_authenticated:
        return render(request,'home.html')
    else:
        return redirect('/Usuarios/login')'''
def home(request):
    if request.user.is_authenticated:        
      
        # Obtén todos los proveedores
        proveedores = Proveedor.objects.all()

        # Recorre cada proveedor y muestra sus productos
        for proveedor in proveedores:
            print(f"Proveedor: {proveedor.Nombre}")
            productos = proveedor.productos_set.all()  # Obtén los productos de cada proveedor
            
            for producto in productos:
                print(f"  Producto: {producto.Nombre}, Precio: {producto.Precio}, Cantidad: {producto.Cantidad}")
            print("---")
                    
        return render(request,'home.html')
    else:
        return redirect('/Usuarios/login')

#region proveedores
def InsertarProveedor(request):
    if request.method == 'POST':
        if request.POST.get('nombre') and request.POST.get('direccion') and request.POST.get('nit') and request.POST.get('email') and request.POST.get('observaciones'):
            nombre=request.POST.get('nombre')
            direccion=request.POST.get('direccion')
            nit=request.POST.get('nit')
            email=request.POST.get('email')
            observaciones=request.POST.get('observaciones')

            insertar= connection.cursor()
            insertar.execute("CALL sp_insertarproveedor(%s,%s,%s,%s,%s)",(nombre,direccion,nit,email,observaciones))
            return redirect('/Proveedor/listado') #coinside con path('Proveedor/listado',ListadoProveedores),
        else:
            nombre=request.POST.get('nombre')
            direccion=request.POST.get('direccion')
            nit=request.POST.get('nit')
            email=request.POST.get('email')
            observaciones=request.POST.get('observaciones')
            mensaje='Favor llenar los datos faltantes'
            return render(request,'Proveedor/insertarproveedor.html',{'nombre':nombre,'direccion':direccion,'nit':nit,'email':email,'observaciones':observaciones,'mensaje':mensaje})
        
    else:
        return render(request, 'Proveedor/insertarproveedor.html')


def ListadoProveedores(request):
    proveedores=connection.cursor()
    proveedores.execute("CALL sp_listadoproveedores()")
    return render(request,'Proveedor/listadoproveedores.html',{'proveedores':proveedores})

def ActualizarProveedor(request, idproveedor):
    if request.method == 'POST':
        if request.POST.get('nombre') and request.POST.get('direccion') and request.POST.get('nit') and request.POST.get('email') and request.POST.get('observaciones'):
            nombre=request.POST.get('nombre')
            direccion=request.POST.get('direccion')
            nit=request.POST.get('nit')
            email=request.POST.get('email')
            observaciones=request.POST.get('observaciones')

            actualizar= connection.cursor()            
            actualizar.execute("CALL sp_actualizarproveedor(%s,%s,%s,%s,%s,%s)",(idproveedor,nombre,direccion,nit,email,observaciones))

            return redirect('/Proveedor/listado') #coinside con path('Proveedor/listado',ListadoProveedores),
    else:
        proveedor = connection.cursor()
        proveedor.execute("CALL sp_consultarunproveedor(%s)", [idproveedor])
        #proveedor.execute("CALL sp_consultarunproveedor('"+ idproveedor+"')")
        return render(request, 'Proveedor/actualizarproveedor.html',{'proveedor':proveedor})

def EliminarProveedor(request):
    idproveedor= request.POST.get('idproveedor')
    proveedor = connection.cursor()
    proveedor.execute("CALL sp_eliminarunproveedor(%s)", [idproveedor])
    return redirect('/Proveedor/listado')

#endregion

#region productos
def InsertarProducto(request):
    if request.method == 'POST':
        if request.POST.get('nombre') and request.POST.get('precio') and request.FILES['foto'] and request.POST.get('cantidad') and request.POST.get('descripcion') and request.POST.get('fecha') and request.POST.get('proveedor_id'):
            producto = Productos()
            producto.Nombre= request.POST.get('nombre')
            producto.Precio= request.POST.get('precio')
            producto.Foto= request.FILES['foto']
            imagen= FileSystemStorage()
            imagen.save(producto.Foto.name, producto.Foto)
            
            producto.Cantidad= request.POST.get('cantidad')
            producto.Descripcion= request.POST.get('descripcion')
            producto.Fecha= request.POST.get('fecha')
            #cuando utilizamos ORM en una relación se busca el objeto completo
            producto.proveedor= Proveedor.objects.get(id=request.POST.get('proveedor_id'))
            producto.save()
            return redirect('/Producto/listado')
    else:      
        proveedores= Proveedor.objects.all() #select * from proveedor
        return render(request,'Productos/insertarproducto.html',{'proveedores':proveedores}) #esta ruta es una dirección física

def ListadoProductos(request):
    productos= Productos.objects.all()
    return render(request,'Productos/listadoproductos.html',{'productos':productos})

def ActualizarProducto(request, idproducto):
    if request.method == 'POST':
        if request.POST.get('nombre') and request.POST.get('precio') and request.POST.get('cantidad') and request.POST.get('descripcion') and request.POST.get('fecha') and request.POST.get('proveedor_id'):
            producto = Productos()
            producto.id =idproducto
            producto.Nombre= request.POST.get('nombre')
            producto.Precio= request.POST.get('precio')
            try:
                if request.FILES['foto']:
                    producto.Foto= request.FILES['foto']
                    imagen= FileSystemStorage()
                    #opcional borrar foto vieja
                    imagen.delete(request.POST.get('foto_anterior'))
                    imagen.save(producto.Foto.name, producto.Foto)
            except:
                producto.Foto= request.POST.get('foto_anterior')                
                #imagen= FileSystemStorage()
                #imagen.save(producto.Foto.name, producto.Foto)
            
            producto.Cantidad= request.POST.get('cantidad')
            producto.Descripcion= request.POST.get('descripcion')
            producto.Fecha= request.POST.get('fecha')
            #cuando utilizamos ORM en una relación se busca el objeto completo
            producto.proveedor= Proveedor.objects.get(id=request.POST.get('proveedor_id'))
            producto.save()
            return redirect('/Producto/listado')
    else:      
        proveedores = Proveedor.objects.all()
        producto= Productos.objects.filter(id=idproducto)
        return render(request, 'Productos/actualizarproducto.html',{'proveedores':proveedores,'producto':producto})

def EliminarProducto(request):
    producto= Productos()
    producto.id= request.POST.get('idproducto')
    producto.delete()
    borrar = FileSystemStorage()
    borrar.delete(request.POST.get('foto'))
    return redirect('/Producto/listado')

def ApiProducto(request):
    id_producto= json.loads(request.body)
    idproducto= id_producto.get('idproducto')    
    producto= Productos.objects.filter(id=idproducto)
    proveedor=""

    for p in producto:
        proveedor= p.proveedor.Nombre

    productojson= serialize('json',producto)
    producto_data= json.loads(productojson)

    for p in producto_data:
        p['fields']['Nombreproveedor']= proveedor
    producto_json_actualizado= json.dumps(producto_data)
    return HttpResponse(producto_json_actualizado,content_type='application/json')

#endregion

#region login
def loginusuario(request):
    if request.method=='POST':
        if request.POST.get('username') and request.POST.get('password'):
            user= authenticate(username=request.POST.get('username'),password=request.POST.get('password'))
            if user is not None:
                login(request,user)
                return redirect('/')
            else:
                mensajeerror='Usuario o contraseña incorrectas, Intente de nuevo'
                return render(request,'Usuarios/login.html',{'mensajeerror':mensajeerror})
    else:
        return render(request,'Usuarios/login.html') #el render debe ser ruta fisica del html sin / al inicio

def RegistrarUsuario(request):
    if request.method == 'POST':
        if request.POST.get('username') and request.POST.get('password') and request.POST.get('first_name') and request.POST.get('last_name') and request.POST.get('email'):
            user = User.objects.create_user(request.POST.get('username'), request.POST.get('email'),request.POST.get('password'))
            user.first_name=request.POST.get('first_name')
            user.last_name= request.POST.get('last_name')
            user.save()
            return redirect('/Usuarios/login') #el redirect debe coincidir con la ruta del archivo urls.py

def logoutusuario(request):
    logout(request)
    return redirect('/Usuarios/login')




#endregion