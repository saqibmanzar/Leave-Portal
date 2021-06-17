from typing import Optional
import datetime
import mongoengine


class Owner(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)
    name = mongoengine.StringField(required=True)
    email = mongoengine.StringField(required=True)
    password = mongoengine.StringField(required=True)
    description = mongoengine.StringField()
    publication = mongoengine.ListField()
    grants = mongoengine.ListField()
    awards = mongoengine.ListField()
    teaching = mongoengine.ListField()
    meta = {
        'db_alias': 'core',
        'collection': 'owners'
    }


active_account: Optional[Owner] = None


def updateInfo(email, pub):
    Owner.objects(email=email).update_one(set__description=pub)


def deletePublication(email, pub):
    Owner.objects(email=email).update_one(pull__publication=pub)


def deleteGrants(email, pub):
    Owner.objects(email=email).update_one(pull__grants=pub)


def deleteAwards(email, pub):
    Owner.objects(email=email).update_one(pull__awards=pub)


def deleteTeaching(email, pub):
    Owner.objects(email=email).update_one(pull__teaching=pub)


def addPublication(email, pub):
    Owner.objects(email=email).update_one(push__publication=pub)


def addGrants(email, pub):
    Owner.objects(email=email).update_one(push__grants=pub)


def addAwards(email, pub):
    Owner.objects(email=email).update_one(push__awards=pub)


def addTeaching(email, pub):
    Owner.objects(email=email).update_one(push__teaching=pub)


def find_account_by_email(email: str) -> Owner:
    owner = Owner.objects(email=email).first()
    return owner


def getInfo(email: str):
    owner = find_account_by_email(email)
    info = {

        'publication': owner.publication,
        'grants': owner.grants,
        'awards': owner.awards,
        'teaching': owner.teaching,
        'description': owner.description

    }
    return info


def create_account(name, email, password) -> Owner:
    owner = Owner()
    owner.name = name
    owner.email = email
    owner.password = password
    owner.save()
    return owner
