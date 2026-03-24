from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.places.models import Place
from .forms import AddToFolderForm, FavoriteFolderForm
from .models import FavoriteFolder, FavoriteItem
from .services import get_or_create_liked_folder


@login_required
def folders_list_view(request):
    get_or_create_liked_folder(request.user)
    folders = FavoriteFolder.objects.filter(user=request.user).prefetch_related('items__place')
    form = FavoriteFolderForm()

    return render(request, 'favorites/folders.html', {
        'folders': folders,
        'form': form,
    })


@login_required
def folder_detail_view(request, folder_id):
    folder = get_object_or_404(
        FavoriteFolder.objects.prefetch_related('items__place__images'),
        id=folder_id,
        user=request.user
    )

    return render(request, 'favorites/folder_detail.html', {
        'folder': folder,
    })


@login_required
@require_POST
def create_folder_view(request):
    form = FavoriteFolderForm(request.POST)

    if form.is_valid():
        folder = form.save(commit=False)
        folder.user = request.user
        folder.save()

    return redirect('favorite_folders')


@login_required
@require_POST
def add_to_folder_view(request, place_id):
    place = get_object_or_404(Place, id=place_id, is_published=True)
    form = AddToFolderForm(request.POST, user=request.user)

    if form.is_valid():
        folder = form.cleaned_data.get('folder')
        new_folder_name = (form.cleaned_data.get('new_folder_name') or '').strip()

        if new_folder_name:
            folder, _ = FavoriteFolder.objects.get_or_create(
                user=request.user,
                name=new_folder_name
            )

        if folder:
            FavoriteItem.objects.get_or_create(
                folder=folder,
                place=place
            )

    return redirect(request.META.get('HTTP_REFERER', 'favorite_folders'))


@login_required
@require_POST
def remove_from_folder_view(request, item_id):
    item = get_object_or_404(
        FavoriteItem.objects.select_related('folder'),
        id=item_id,
        folder__user=request.user
    )
    folder_id = item.folder.id
    item.delete()

    return redirect('favorite_folder_detail', folder_id=folder_id)


@login_required
def add_to_folder_modal_view(request, place_id):
    place = get_object_or_404(Place, id=place_id, is_published=True)
    form = AddToFolderForm(user=request.user)

    return render(request, 'favorites/add_to_folder_form.html', {
        'place': place,
        'form': form,
    })
