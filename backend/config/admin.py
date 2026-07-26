from django.conf import settings
from django.contrib import admin
from django.contrib.admin.apps import AdminConfig


class CustomAdminSite(admin.AdminSite):
    site_header = settings.ADMIN_SITE_HEADER
    site_title = settings.ADMIN_SITE_TITLE
    index_title = settings.ADMIN_INDEX_TITLE

    def get_app_list(self, request, app_label=None):
        app_list = self._build_app_dict(request)

        if not hasattr(settings, "ADMIN_REORDER"):
            return sorted(app_list.values(), key=lambda x: x["name"].lower())

        app_dict = {}
        for app in app_list.values():
            if not app.get("has_module_perms"):
                continue

            app_dict[app["app_label"]] = {
                model["object_name"]: model for model in app["models"]
            }

        final_app_list = []
        for section_config in settings.ADMIN_REORDER:
            section_label = section_config.get("label", "UNKNOWN")
            section_models = []

            for key_path in section_config.get("models", []):
                app_key, model_key, *_ = *key_path.split("."), None
                if app_key not in app_dict:
                    continue

                if not model_key:
                    section_models.extend(app_dict[app_key].values())
                    continue

                if model_key not in app_dict[app_key]:
                    continue

                section_models.append(app_dict[app_key][model_key])

            if section_models:
                final_app_list.append(
                    {
                        "name": section_label,
                        "app_label": app_key,
                        "models": section_models,
                    }
                )

        return final_app_list


class CustomAdminConfig(AdminConfig):
    default_site = "config.admin.CustomAdminSite"
