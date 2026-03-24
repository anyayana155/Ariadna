from .models import FavoriteFolder, FavoriteItem


LIKED_FOLDER_NAME = 'Понравилось'


def get_or_create_liked_folder(user):
    folder, _ = FavoriteFolder.objects.get_or_create(
        user=user,
        name=LIKED_FOLDER_NAME
    )
    return folder


def add_place_to_folder(folder, place):
    item, created = FavoriteItem.objects.get_or_create(
        folder=folder,
        place=place
    )
    return item, created


def add_place_to_liked_folder(user, place):
    folder = get_or_create_liked_folder(user)
    return add_place_to_folder(folder, place)
