"""
This file contains the schema for the CRM API.
"""

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django_filters.rest_framework import DjangoFilterBackend
# from .mutations import CreateCustomer, BulkCreateCustomers, CreateProduct, CreateOrder

from .filters import CustomerFilter, ProductFilter, OrderFilter
from .models import Customer, Product, Order
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

# Use standard DjangoObjectType with Relay Node interface


# Define a validator for the phone format
phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$', 
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

class CustomerType(DjangoObjectType):
    """
    Define Customer fields
    """

    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,)

class ProductType(DjangoObjectType):
    """
    Define Product fields
    """

    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,)


class OrderType(DjangoObjectType):
    """
    Define Order fields
    """
    
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount")
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)

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
    price = graphene.Decimal(required=True)
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
        try:
            validated_phone = CreateCustomer.validate_phone(customer.phone)
            customer=Customer.objects.create(
                name=customer.name,
                email=customer.email,
                phone=validated_phone,
            )
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
    
    @staticmethod
    def validate_phone(phone):
        """
        Validate the phone number
        """
        phone_regex(phone) # raise ValidationError if phone is not valid
        return phone
 

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
        customer = Customer.objects.filter(pk=order.customer)
        products = Product.objects.filter(pk__in=order.products)

        if not customer.exists():
            raise ValidationError("Customer not found")
        
        if not products.exists():
            raise ValidationError("Products not found")
        total_amount = sum(product.price for product in products)
        
        try:
            order=Order.objects.create(
                customer=customer.first(),
                total_amount=total_amount,
            )
            order.products.set(products)
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
    errors = graphene.List(graphene.String)

    class Arguments:
        customers = graphene.List(CustomerInput, required=True)

    def mutate(self, info, customers):
        created_customers = []
        errors = []

        for customer_data in customers:
            try:
                validated_phone = CreateCustomer.validate_phone(customer_data.phone)
                # get_or_create to handle unique email validation. 
                # IntegrityError will be raised if the email exists.
                customer, created = Customer.objects.get_or_create(
                    email=customer_data.email,
                    defaults={
                        'name': customer_data.name,
                        'phone': validated_phone
                    }
                )
                if created:
                    created_customers.append(customer)
                else:
                    errors.append(f"Error creating customer with email '{customer_data.email}': Email already exists.")  
            except ValidationError as e:
                errors.append(f"Error creating customer: {e}")
            except IntegrityError:
                errors.append("Error creating customer with email '{customer_data.email}': Email already exists.")
            except Exception as e:
                errors.append(f"Error creating customer: {e}")
        
        return BulkCreateCustomers(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    """
    Create a new product
    """

    product = graphene.Field(ProductType)
    total_amount = graphene.Float()
    message = graphene.String()

    class Arguments:
        product = ProductInput(required=True)

    def mutate(self, info, product):
        """
        Create a new product
        """
        validated_stock = CreateProduct.validate_stock(product.stock)
        validated_price = CreateProduct.validate_price(product.price)

        try: 
            product = Product.objects.create(
                name=product.name,
                price=validated_price,
                stock=validated_stock,
            )
        except ValidationError as e:
            return CreateProduct(
                product=None, total_amount=0, message=str(e)
            )
        except Exception as e:
            return CreateProduct(
                product=None, total_amount=0, message=str(e)
            )
        total_amount = validated_price * validated_stock
        return CreateProduct(
            product=product, total_amount=total_amount, message="Product created successfully"   
        )
    
    @staticmethod   
    def validate_stock(stock):
        """
        Validate the stock
        """
        if stock <= 0:
            raise ValidationError("Stock must be greater than 0")
        return stock
    
    @staticmethod
    def validate_price(price):
        """
        Validate the price
        """
        if price <= 0:
            raise ValidationError("Price must be greater than 0")
        return price


class Query(graphene.ObjectType):
    """
    Define Query fields
    """

    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)

    customer = graphene.Field(CustomerType, id=graphene.ID(required=True))
    product = graphene.Field(ProductType, id=graphene.ID(required=True))
    order = graphene.Field(OrderType, id=graphene.ID(required=True))

    
    def resolve_customer(self, info, id):
        """
        Get a customer by id
        """
        try:
            return Customer.objects.get(pk=id)
        except Customer.DoesNotExist as e:
            raise Exception(f"Error getting customer: {e}")

    def resolve_product(self, info, id):
        """
        Get a product by id
        """
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist as e:
            raise Exception(f"Error getting product: {e}")

    def resolve_order(self, info, id):
        """
        Get an order by id
        """
        try:
            return Order.objects.get(pk=id)
        except Exception as e:
            raise Exception(f"Error getting order: {e}")

class Mutation(graphene.ObjectType):
    """
    Define Mutation fields
    """

    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()  


schema = graphene.Schema(query=Query, mutation=Mutation)
