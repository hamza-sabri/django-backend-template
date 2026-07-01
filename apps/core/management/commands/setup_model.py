"""
Generate a full DRF API for an existing model, then makemigrations.

    python manage.py setup_model catalog Product

Given a model you've already written in apps/catalog/models.py, this generates:
  - a ModelSerializer          (apps/catalog/serializers.py)
  - a ModelViewSet             (apps/catalog/views.py)  auth + pagination wired
  - a router registration      (apps/catalog/urls.py)   -> /api/v1/products/
  - an admin registration      (apps/catalog/admin.py)  list_display/search/filter
and runs `makemigrations <app>` for you.

It is idempotent: classes that already exist are left untouched (re-running is
safe). Field lists are inferred from the model, so re-run after adding fields
only if you want the admin/search lists refreshed (delete the block first).
"""
from pathlib import Path

from django.apps import apps as django_apps
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import models as dj

from apps.core import scaffold


def _plural(name: str) -> str:
    lower = name.lower()
    if lower.endswith(("s", "x", "z", "ch", "sh")):
        return lower + "es"
    if lower.endswith("y") and lower[-2:-1] not in "aeiou":
        return lower[:-1] + "ies"
    return lower + "s"


class Command(BaseCommand):
    help = "Scaffold DRF serializer, viewset, router and admin for a model, then makemigrations."

    def add_arguments(self, parser):
        parser.add_argument("app_label", help="App label, e.g. catalog")
        parser.add_argument("model_name", help="Model class name, e.g. Product")
        parser.add_argument(
            "--no-migrations",
            action="store_true",
            help="Do not run makemigrations afterwards.",
        )

    def handle(self, *args, **opts):
        app_label = opts["app_label"]
        model_name = opts["model_name"]

        try:
            model = django_apps.get_model(app_label, model_name)
        except LookupError:
            raise CommandError(
                f"Model '{model_name}' not found in app '{app_label}'. "
                f"Define it in apps/{app_label}/models.py first (then re-run)."
            )

        app_dir = Path(django_apps.get_app_config(app_label).path)
        Model = model.__name__

        introspection = self._introspect(model)
        prefix = _plural(Model)
        basename = Model.lower()

        created = []
        created += self._write_serializer(app_dir, Model, introspection)
        created += self._write_viewset(app_dir, Model, introspection)
        created += self._write_route(app_dir, Model, prefix, basename)
        created += self._write_admin(app_dir, Model, introspection)

        if created:
            self.stdout.write(self.style.SUCCESS(f"Generated for {app_label}.{Model}:"))
            for item in created:
                self.stdout.write(f"  + {item}")
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Nothing new to generate for {app_label}.{Model} "
                    "(serializer/viewset/route/admin already present)."
                )
            )

        if not opts["no_migrations"]:
            self.stdout.write("Running makemigrations...")
            call_command("makemigrations", app_label)

        self.stdout.write(
            self.style.SUCCESS(f"Done. Endpoint: /api/v1/{prefix}/  (apply with migrate).")
        )

    # -- introspection -------------------------------------------------------
    def _introspect(self, model) -> dict:
        read_only, display, search, list_filter = [], [], [], []
        for f in model._meta.fields:
            name = f.name
            if f.primary_key or getattr(f, "auto_now", False) or getattr(f, "auto_now_add", False):
                read_only.append(name)
            if not isinstance(f, (dj.TextField, dj.JSONField, dj.BinaryField)):
                display.append(name)
            if isinstance(f, (dj.CharField, dj.TextField)):  # CharField covers Email/Slug/URL
                search.append(name)
            if isinstance(f, (dj.BooleanField, dj.DateField, dj.DateTimeField)) or getattr(f, "choices", None):
                list_filter.append(name)
        return {
            "read_only": read_only,
            "display": display[:6],
            "search": search[:6],
            "list_filter": list_filter[:5],
        }

    # -- writers (each returns [] or [label]) --------------------------------
    def _write_serializer(self, app_dir, Model, info) -> list[str]:
        path = app_dir / "serializers.py"
        content = scaffold.ensure_anchor(path, scaffold.SERIALIZERS_HEADER)
        if f"class {Model}Serializer(" in content:
            return []
        ro = ", ".join(repr(x) for x in info["read_only"])
        block = [
            "",
            "",
            f"class {Model}Serializer(serializers.ModelSerializer):",
            "    class Meta:",
            f"        model = models.{Model}",
            '        fields = "__all__"',
            f"        read_only_fields = [{ro}]",
        ]
        scaffold.write(path, scaffold.insert_before_anchor(content, scaffold.SERIALIZERS_ANCHOR, block))
        return [f"serializers.py: {Model}Serializer"]

    def _write_viewset(self, app_dir, Model, info) -> list[str]:
        path = app_dir / "views.py"
        content = scaffold.ensure_anchor(path, scaffold.VIEWS_HEADER)
        if f"class {Model}ViewSet(" in content:
            return []
        search = ", ".join(repr(x) for x in info["search"])
        block = [
            "",
            "",
            f"class {Model}ViewSet(viewsets.ModelViewSet):",
            f"    queryset = models.{Model}.objects.all()",
            f"    serializer_class = serializers.{Model}Serializer",
            "    permission_classes = [permissions.IsAuthenticatedOrReadOnly]",
            f"    search_fields = [{search}]",
            '    ordering_fields = "__all__"',
        ]
        scaffold.write(path, scaffold.insert_before_anchor(content, scaffold.VIEWSETS_ANCHOR, block))
        return [f"views.py: {Model}ViewSet"]

    def _write_route(self, app_dir, Model, prefix, basename) -> list[str]:
        path = app_dir / "urls.py"
        content = scaffold.ensure_anchor(path, scaffold.URLS_HEADER)
        register = f'router.register(r"{prefix}", views.{Model}ViewSet, basename="{basename}")'
        if register in content:
            return []
        scaffold.write(path, scaffold.insert_before_anchor(content, scaffold.ROUTES_ANCHOR, [register]))
        return [f"urls.py: /{prefix}/"]

    def _write_admin(self, app_dir, Model, info) -> list[str]:
        path = app_dir / "admin.py"
        content = scaffold.ensure_anchor(path, scaffold.ADMIN_HEADER)
        if f"class {Model}Admin(" in content:
            return []
        display = ", ".join(repr(x) for x in info["display"])
        search = ", ".join(repr(x) for x in info["search"])
        lfilter = ", ".join(repr(x) for x in info["list_filter"])
        block = [
            "",
            "",
            f"@admin.register(models.{Model})",
            f"class {Model}Admin(admin.ModelAdmin):",
            f"    list_display = [{display}]",
            f"    search_fields = [{search}]",
            f"    list_filter = [{lfilter}]",
        ]
        scaffold.write(path, scaffold.insert_before_anchor(content, scaffold.ADMIN_ANCHOR, block))
        return [f"admin.py: {Model}Admin"]
