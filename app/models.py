# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.parser import parse
import json
from werkzeug.security import generate_password_hash, check_password_hash
from elasticsearch_dsl import Document, Keyword, Boolean, Date, Integer, Text, Completion, \
    FacetedSearch, TermsFacet, DateHistogramFacet, Double


class Client(Document):
    """
    Client model
    """
    client_id = Keyword()
    secret_hash = Keyword()
    email = Keyword()
    confirmed = Boolean()
    favorite_genders = Keyword()

    class Index:
        name = 'client'

    @property
    def secret(self):
        return self.secret_hash

    @secret.setter
    def secret(self, pwd):
        self.secret_hash = generate_password_hash(pwd)

    def check_secret(self, pwd):
        return check_password_hash(self.secret_hash, pwd)

    @property
    def offers_query(self):
        return BookOffer.search().query('match', client_id=self.client_id)

    @property
    def offers(self):
        return self.offers_query.execute()

    def to_dict(self, include_id=False, include_offers=False, include_meta=False, skip_empty=True):
        base = super().to_dict(include_meta=include_meta, skip_empty=skip_empty)

        if include_id:
            base['id'] = self.meta.id

        if include_offers:
            base['offers'] = [o.to_dict(include_id=True) for o in self.offers]

        return base


class BookOffer(Document):
    """
    Book offer model
    """
    created_at = Date()
    client_id = Keyword()
    book_id = Keyword()
    price = Double()

    class Index:
        name = 'books_offers'

    @staticmethod
    def from_dict(data):
        return BookOffer(
            created_at=data['created_at'],
            client_id=data['client_id'],
            book_id=data['book_id'],
            price=data['price']
        )

    def to_dict(self, include_id=False, include_meta=False, skip_empty=True):
        base = super().to_dict(include_meta=include_meta, skip_empty=skip_empty)

        if include_id:
            base['id'] = self.meta.id

        return base


class Book(Document):
    """
    Book model
    """
    publication = Date()
    isbn = Keyword()

    name = Text(fields={'keyword': Keyword()})
    name_suggest = Completion()

    authors = Keyword()
    cover = Keyword()
    editor = Keyword()
    pages = Integer()
    description = Keyword()
    genders = Keyword()

    last_offer = Date()
    min_price = Double()
    max_price = Double()
    nb_offers = Integer()

    class Index:
        name = 'books'

    @property
    def offers_query(self):
        return BookOffer.search().query('match', book_id=self.meta.id)

    @property
    def offers(self):
        return self.offers_query.execute()

    def add_offer(self, client_id, price):
        """
        Add offer
        """
        now = datetime.now()
        offer = BookOffer.from_dict({
            'created_at': now,
            'client_id': client_id,
            'book_id': self.meta.id,
            'price': price
        })
        offer.save()

        self.last_offer = now

        if self.min_price is None:
            self.min_price = price
        elif price < self.min_price:
            self.min_price = price

        if self.max_price is None:
            self.max_price = price
        elif price > self.max_price:
            self.max_price = price

        self.nb_offers += 1
        self.save()

    def remove_offer(self, offer_id):
        """
        Remove offer
        """
        offer = BookOffer.get(id=offer_id, ignore=404)
        if offer is None:
            raise Exception('Offer #{0} not found'.format(offer_id))

        if offer.book_id != self.meta.id:
            raise Exception('Book #{0} not contains Offer #{1}'.format(self.meta.id, offer_id))

        offer.delete()
        self.nb_offers -= 1

        if self.nb_offers != 0:
            prices = []
            dates = []

            for offer in self.offers:
                prices.append(offer.price)
                dates.append(offer.created_at)

            self.min_price = min(prices)
            self.max_price = max(prices)
            self.last_offer = max(dates)

        else:
            self.min_price = None
            self.max_price = None
            self.last_offer = None

        self.save()

    @staticmethod
    def from_dict(data):
        return Book(
            publication=parse(data['publication']),
            isbn=data['isbn'],
            name=data['name'],
            name_suggest=data['name'],
            authors=data['authors'],
            cover=data['cover'],
            editor=data['editor'],
            pages=data['pages'],
            description=data.get('description'),
            genders=data['genders'],
            nb_offers=0
        )

    def to_dict(self, include_id=False, include_offers=False, include_meta=False, skip_empty=True):
        base = super().to_dict(include_meta=include_meta, skip_empty=skip_empty)

        if include_id:
            base['id'] = self.meta.id

        if include_offers:
            base['offers'] = [o.to_dict(include_id=True) for o in self.offers]

        return base


class BookSearch(FacetedSearch):
    """
    Book search
    """
    doc_types = [Book,]
    fields = ['authors', 'name', 'genders', 'editor']

    facets = {
        'authors': TermsFacet(fields='authors'),
        'genders': TermsFacet(fields='genders'),
        'editors': TermsFacet(fields='editors'),
        'publication': DateHistogramFacet(field='publication', interval='year')
    }
