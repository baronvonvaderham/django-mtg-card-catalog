from django.contrib import admin

from .models import Card, CardSet, CardPrice, ScryfallCard


class CardAdmin(admin.ModelAdmin):
    readonly_fields = ("tcg_product_id", "set",)


class CardSetAdmin(admin.ModelAdmin):
    readonly_fields = ("tcgplayer_group_id", "code",)


class CardPriceAdmin(admin.ModelAdmin):
    readonly_fields = ("card", "date")


class ScryfallCardAdmin(admin.ModelAdmin):
    pass


admin.site.register(Card, CardAdmin)
admin.site.register(CardSet, CardSetAdmin)
admin.site.register(CardPrice, CardPriceAdmin)
admin.site.register(ScryfallCard, ScryfallCardAdmin)
