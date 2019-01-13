# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.parser import parse
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
    balance = Double()

    class Index:
        name = 'clients'

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
            base['offers'] = []
            base['purchased'] = []
            for offer in self.offers:
                if not offer.purchased:
                    base['offers'].append(offer.to_dict(include_id=True))
                else:
                    base['purchased'].append(offer.to_dict(include_id=True))

        return base


class BookOffer(Document):
    """
    Book offer model
    """
    created_at = Date()
    client_id = Keyword()
    book_id = Keyword()
    price = Double()

    purchased = Boolean()
    buyer_id = Keyword()

    class Index:
        name = 'books_offers'

    @staticmethod
    def from_dict(data):
        return BookOffer(
            created_at=data['created_at'],
            client_id=data['client_id'],
            book_id=data['book_id'],
            price=data['price'],
            purchased=data.get('purchased', False),
            buyer_id=data.get('buyer_id')
        )

    def to_dict(self, include_id=False, include_meta=False, skip_empty=True):
        base = super().to_dict(include_meta=include_meta, skip_empty=skip_empty)

        if include_id:
            base['id'] = self.meta.id

        return base

    def delete(self, using=None, index=None, **kwargs):
        book_id = self.book_id

        super().delete(using=using, index=index, **kwargs)

        if book_id is not None:
            book = Book.get(id=book_id, ignore=404)

            if book is not None:
                book.update_offers_summary()


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
        offer.save(refresh=True)

        self.update_offers_summary()

        return offer

    def update_offers_summary(self):
        self.nb_offers = 0
        self.min_price = None
        self.max_price = None
        self.last_offer = None

        prices = []
        dates = []

        for offer in self.offers:
            if not offer.purchased:
                prices.append(offer.price)
                dates.append(offer.created_at)
                self.nb_offers += 1

        if self.nb_offers != 0:
            self.min_price = min(prices)
            self.max_price = max(prices)
            self.last_offer = max(dates)

        self.save(refresh=True)

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
            base['offers'] = []
            for offer in self.offers:
                if not offer.purchased:
                    base['offers'].append(offer.to_dict(include_id=True))

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
