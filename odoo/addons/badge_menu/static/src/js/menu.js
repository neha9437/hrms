 odoo.define('badge_menu', function (require) {
    'use strict';

    var Menu = require('web.Menu');
    var Class = require('web.Class');
    var SearchView = require('web.SearchView');
    var core = require('web.core');
    var config = require('web.config');
    var FieldOne2Many = core.form_widget_registry.get('one2many');
    var ViewManager = require('web.ViewManager');
    var session = require('web.session');
    var QWeb = core.qweb;

    Menu.include({
        on_change_leaf_menu: function (id) {
            var self = this;
            var $clicked_menu = this.$secondary_menus.find('a[data-menu=' + id + ']');

            // Fetch the menu leaves ids in order to check if they need a 'needaction'
            var $secondary_menu = $clicked_menu.parents('.oe_secondary_menu');
            var $menu_leaves = $secondary_menu.children().find('.oe_menu_leaf');
            var menu_ids = _.map($menu_leaves, function (leave) {
                return parseInt($(leave).attr('data-menu'), 10);
            });
            self.do_load_needaction(menu_ids).then(function () {
                //self.trigger("need_action_reloaded");
            });
        },
        /* Overload to collapse unwanted visible submenus
         * @param allow_open bool Switch to allow submenus to be opened
         */
        open_menu: function (id, allowOpen) {
            this._super(id);
            this.on_change_leaf_menu(id);
        },
        do_load_needaction: function (menu_ids) {
            var self = this;
            menu_ids = _.compact(menu_ids);
            if (_.isEmpty(menu_ids)) {
                return $.when();
            }
            return session.rpc("/web/menu/load_needaction", {
                'menu_ids': menu_ids
            }).done(function (r) {
                self.on_needaction_loaded(r);
            });
        },
        on_needaction_loaded: function (data) {
            var self = this;
            this.needaction_data = data;
            _.each(this.needaction_data, function (item, menu_id) {
                var $item = self.$secondary_menus.find('a[data-menu="' + menu_id + '"]');
                $item.find('.badge').remove();
                if (item.needaction_counter && item.needaction_counter > 0) {
                    $item.append(QWeb.render("Menu.needaction_counter", {
                        widget: item
                    }));
                }
            });
        },
        do_reload_needaction: function () {
            var self = this;
            if (self.current_menu) {
                self.do_load_needaction([self.current_menu]).then(function () {
                    //self.trigger("need_action_reloaded");
                });
            }
        },

    });

    return {
        'Menu': Menu,
    };

});