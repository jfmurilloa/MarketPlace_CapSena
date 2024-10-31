from django.db import models

class Proveedor(models.Model):
    Nombre= models.CharField(max_length=150)
    Direccion= models.CharField(max_length=255)
    Nit=models.CharField(max_length=20)
    Email=models.CharField(max_length=200)
    Observaciones=models.CharField(max_length=255)
    Estado=models.CharField(max_length=10)

    class Meta:
        db_table= 'proveedor' #nombre de la tabla en la base de datos

class Productos(models.Model):
    Nombre= models.CharField(max_length=255)
    Precio= models.BigIntegerField()
    Foto= models.CharField(max_length=255)
    Cantidad= models.BigIntegerField()
    Descripcion= models.CharField(max_length=255)
    Fecha= models.CharField(max_length=255)
    proveedor = models.ForeignKey(Proveedor,on_delete=models.CASCADE)
    class Meta:
        db_table= 'productos'


