"""
This file contains the schema for the CRM API.
"""

import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.db import IntegrityError
from django.core.exceptions import ValidationError


class CustomerType(DjangoObjectType):
    """
    Define Customer fields
    """

    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class ProductType(DjangoObjectType):
    """
    Define Product fields
    """

    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")


class OrderType(DjangoObjectType):
    """
    Define Order fields
    """
    
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "order_date")
    

class CustomerInput(graphene.InputObjectType):
    """
    Define Customer input fields
    """

    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=True)

class OrderInput(graphene.InputObjectType):
    """
    Define Order input fields
    """

    customer = graphene.Int(required=True)
    products = graphene.List(graphene.Int, required=True)
    order_date = graphene.Date(required=True)

class BulkCreateCustomersInput(graphene.InputObjectType):
    """
    Define BulkCreateCustomers input fields
    """

    customers = graphene.List(CustomerInput)

class ProductInput(graphene.InputObjectType):
    """
    Define Product input fields
    """

    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(required=True)


class CreateProduct(graphene.Mutation):
    """
    Create a new product
    """

    product = graphene.Field(ProductType)
    message = graphene.String()

    class Arguments:
        product = ProductInput(required=True)

    def mutate(self, info, product):
        """
        Create a new product
        """
        product = Product.objects.create(
            name=product.name,
            price=product.price,
            stock=product.stock,
        )
        return CreateProduct(
            product=product, message="Product created successfully"
        )


class BulkCreateProductsInput(graphene.InputObjectType):
    """
    Define BulkCreateProducts input fields
    """

    products = graphene.List(ProductInput)

class CreateCustomer(graphene.Mutation):
    """
    Define CreateCustomer fields
    """

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    class Arguments:
        customer = CustomerInput(required=True)

    def mutate(self, info, customer = None):
        """
        Create a new customer
        """
        customer = Customer(
            name=customer.name,
            email=customer.email,
            phone=customer.phone,
        )

        try:
            customer.full_clean()
            customer.save()
        except ValidationError as e:
            return CreateCustomer(
                customer=None, message=str(e)
            )
        except IntegrityError:
            return CreateCustomer(
                customer=None, message="Email already exists"
            )
        except Exception as e:
            return CreateCustomer(
                customer=None, message=str(e)
            )
        return CreateCustomer(
            customer=customer, message="Customer created successfully"
        )


class CreateOrder(graphene.Mutation):
    """
    Create a new order
    """

    order = graphene.Field(OrderType)
    message = graphene.String()

    class Arguments:
        order = OrderInput(required=True)

    def mutate(self, info, order = None):
        """
        Create a new order
        """
        order = Order(
            customer=order.customer,
            products=order.products,
            order_date=order.order_date,
        )
        
        try:
            order.full_clean()
            order.save()
        except ValidationError as e:
            return CreateOrder(
                order=None, message=str(e)
            )
        except Exception as e:
            return CreateOrder(
                order=None, message=str(e)
            )
        return CreateOrder(
            order=order, message="Order created successfully"
        )


class BulkCreateCustomers(graphene.Mutation):
    """
    Create multiple customers
    """

    customers = graphene.List(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)
    error_message = graphene.String()

    class Arguments:
        customers = graphene.List(CustomerInput, required=True)

    def mutate(self, info, customers):
        created_customers = []
        errors = []

        for customer_data in customers:
            try:
                # Use get_or_create to handle unique email validation. 
                # IntegrityError will be raised if the email exists.
                customer, created = Customer.objects.get_or_create(
                    email=customer_data.email,
                    defaults={
                        'name': customer_data.name,
                        'phone': customer_data.phone
                    }
                )
                if not created:
                    errors.append(f"Error creating customer with email '{customer_data.email}': Email already exists.")
                else:
                    created_customers.append(customer)
            except IntegrityError:
                errors.append(f"Error creating customer with email '{customer_data.email}': Email already exists.")
            except Exception as e:
                errors.append(f"Error creating customer: {e}")
        
        return BulkCreateCustomers(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    """
    Create a new product
    """

    product = graphene.Field(ProductType)
    message = graphene.String()

    class Arguments:
        product = ProductInput(required=True)

    def mutate(self, info, product):
        """
        Create a new product
        """
        product = Product.objects.create(
            name=product.name,
            price=product.price,
            stock=product.stock,
        )
        return CreateProduct(
            product=product, message="Product created successfully"
        )


class Query(graphene.ObjectType):
    """
    Define Query fields
    """

    all_customers = graphene.List(CustomerType)
    customer = graphene.Field(CustomerType, id=graphene.Int(required=True))
    all_products = graphene.List(ProductType)
    product = graphene.Field(ProductType, id=graphene.Int(required=True))
    all_orders = graphene.List(OrderType)
    order = graphene.Field(OrderType, id=graphene.Int(required=True))

    def resolve_all_customers(self, info):
        """
        Get all customers
        """
        return Customer.objects.all()

    def resolve_customer(self, info, id):
        """
        Get a customer by id
        """
        return Customer.objects.get(id=id)

    def resolve_all_products(self, info):
        """
        Get all products
        """
        return Product.objects.all()

    def resolve_product(self, info, id):
        """
        Get a product by id
        """
        return Product.objects.get(id=id)

    def resolve_all_orders(self, info):
        """
        Get all orders
        """
        return Order.objects.all()

    def resolve_order(self, info, id):
        """
        Get an order by id
        """
        return Order.objects.get(id=id)

class Mutation(graphene.ObjectType):
    """
    Define Mutation fields
    """

    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()

    create_product = CreateProduct.Field()

    create_order = CreateOrder.Field()  


schema = graphene.Schema(query=Query, mutation=Mutation)
