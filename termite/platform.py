# This file is part of Termite Plugins Platform
#    Copyright (C) 2014 Pavle Jonoski
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Termite Platform package. Defines the plugins, plugin container and the platform
interface.
"""

import logging
from termite import metadata
from termite.dependencies import PluginDependenciesManager
from termite.loader import ClassProtocolHandler, PlatformPluginsFinder, register_finder
from termite.plugins.support import PluginLoaderHandler, plugin_references_from_location
from termite.resources import BaseResourceLoader
from termite.tools import Proxy


class Plugin:
    """Base class for all Plugins.

    This is the entry point in the plugin itself. Each plugin MUST expose
    at least one implementation of Plguin.

    """

    STATE_UNINSTALLED = 0x0
    """ The plugin is loaded but the installation has not yet taken place or
    it has been uninstalled.
    """

    STATE_INSTALLED = 0x1
    """The plugin is installed on the platform.

    At this point all dependencies for the plugin had been resolved and satisfied.
    """

    STATE_ACTIVE = 0x2
    """ The plugin has been successfully activated.

    At this point, the call to Plugin.activate(...) has been made and no errors
    were detected.
    """

    STATE_DEACTIVATED = 0x3
    """ The plugin has been deactivated, but it is still available on the platform.
    """

    STATE_DISPOSED = 0x4
    """ The plugin is ready to be removed from the platform.

    This point may have been reached by calling PluginManager.dispose(...) or
    it may be a result of an error during installation (such as dependencies that
    had not been satisfied).

    The plugin will be completely removed from the platform on the next garbage
    collection cycle.
    """

    def activate(self):
        """Called to activate the plugin.

        This method is called once the plugin has been installed and all of the
        declared dependencies have been resolved and are available.

        If the method raises an error, the activation of the plugin will be
        canceled and the plugin will be put in an ERROR state.

        This method is intended to be implemented in a subclass.
        """
        pass

    def deactivate(self):
        """Called to deactivate the plugin.

        This method is called when the plugin is ready to be deactivated and no
        longer will be used by the platform.

        This method is intended to be implemented in a subclass. Typical usage
        would be to free any used resources by the plugin and to perform a final
        shutdown procedure.

        If an error is raised by this method, the plugin will be put in an ERROR
        state.
        """
        pass

    def on_state_change(self, state):
        """Called every time when the plugin state chnages.

        state is the new state of the plugin.
        """
        pass


class PluginContainer:
    """Wrapper around a real plugin instance.

    The platform does not interact directly with the plugin instances, but
    interacts with a PluginContainer instace instead. The plugin container
    provides a sandbox around a plugin and maintains a state and context that is
    of relevance to the plugin platform, but is not directly a concern of the
    plugin itself. This way there is a separation of concerns - the plugin
    handles and performs functions of relevance to the business and the
    container handles the plugin management context.

    The plugin container maintains the plugin state and metadata for the plugin
    itself (version, the manifest file, plugin loader, dependencies etc).
    """
    def __init__(self, plugin_ref, resource_loader, plugin_manager):
        """Creates new instance of a PluginContainer.

        plugin_ref is a refrence to a real plugin, usually a refrence to a
        plugin physical resource. Most of the time this will be a relevant URL
        to the plugin resource itself. The plugin_ref is a unique identifier for
        a particular plugin (it cannot point to more than one plugin and no more
        than one plugin can have the same reference).

        resource_loader the ResourceLoader used to load the actual plugin
        resource. See termite.resources.BaseResourceLoader for more details.

        plugin_manager the PluginManager that manages this plugin container.
        """
        self.loader = resource_loader
        self.plugin_ref = plugin_ref
        self.plugin_manager = plugin_manager
        self.plugin_id = None
        self.manifest = None
        self.dependencies = []
        self.plugin_hooks = []
        self.plugin_state = None
        self.plugin = None
        self.version = None
        self.logger = logging.getLogger('termite.platform.PluginContainer')

    def load(self):
        """Loads the plugin onto the platform.

        Loads the plugin resource using the ResourceManager and initialized the
        plugin state.

        Note that no plugin instances are attempted to be created and no actual
        code from the plugin is executed at this point. This loads the metadata
        descrribing the plugin itself.

        At this point, although the plugin is loaded, it is not yet available
        as a dependency on the platform.
        """
        if self.plugin_state == Plugin.STATE_DISPOSED:
            raise PluginLifecycleException("Plugin already disposed")

        self.plugin = self.loader.load('plugin:' + self.plugin_ref)
        self.manifest = self.plugin.get_manifest()
        self.plugin_id = self.manifest.id
        self.version = self.manifest.version
        self.plugin_state = Plugin.STATE_UNINSTALLED

    def install(self):
        """Installs the plugin onto the platform.

        The plugin dependencies must be available in order for the plugin to be
        installed.

        Once the dependecies are resolved, the plugin hooks are created and the
        plugin state is set to INSTALLED.

        Raises a PluginLifecycleException if the plugin is not in the proper
        state for installation. Refer to the plugin state diagram for the
        allowed states and transitions.
        """
        if self.plugin_state is not Plugin.STATE_UNINSTALLED:
            raise PluginLifecycleException("Cannot install plugin. Invalid state: %s" % str(self.plugin_state))
        try:
            self.resolve_dependencies()
            self.create_hooks()
            self.plugin_state = Plugin.STATE_INSTALLED
            self.notify_state_change(Plugin.STATE_INSTALLED)
        except Exception as e:
            self.plugin_state = Plugin.STATE_DISPOSED
            raise e

    def create_hooks(self):
        """Instantiates the plugin hooks.

        A plugin hook is an object which life-cycle is managed by the platform.
        This is the entry point to to plugin.

        A plugin hook can be specified by type (class). The class must be
        defined in the plugin modules. The hooks are specified in the plugin
        manifest file in the section "Plugin-Classes".
        """
        manifest = self.plugin.get_manifest()
        for hook_class_name in manifest.plugin_classes:
            hook_class = self.loader.load('class:' + hook_class_name)
            hook_inst = hook_class()
            if not isinstance(hook_inst, Plugin):
                hook_inst = Proxy(target=hook_inst)
            self.plugin_hooks.append(hook_inst)

    def resolve_dependencies(self):
        pass

    def dispose_dependencies(self):
        pass

    def activate(self):
        """Activates the plugin.

        A plugin can be activated only it was alerady successfully installed.
        A deactivated plugin may be activated again (but that would mean that
        the plugin was already installed earlier, before the first activation).

        When activated, if the plugin exposes any hooks, on each hook instance
        the method "activate" will be invoked.
        """
        if self.plugin_state is not Plugin.STATE_INSTALLED and self.plugin_state is not Plugin.STATE_DEACTIVATED:
            raise PluginLifecycleException("Cannot activate plugin. Invalid state: %s" % str(self.plugin_state))
        try:
            for hook in self.plugin_hooks:
                hook.activate()
            self.plugin_state = Plugin.STATE_ACTIVE
            self.notify_state_change(Plugin.STATE_ACTIVE)
        except Exception as e:
            self.logger.error("Plugin activation error: %s", e)
            self.plugin_state = Plugin.STATE_DEACTIVATED
            self.notify_state_change(Plugin.STATE_DEACTIVATED)

    def deactivate(self):
        """Deactivates a plugin.

        Only an active plugin can be deactivated. If the plugin is not in ACTIVE
        state, an error would be raised.

        If the plugin exposes any hooks, on each hook instance the method
        "deactivate" will be invoked.
        """
        if self.plugin_state is not Plugin.STATE_ACTIVE:
            raise PluginLifecycleException("Cannot deactivate plugin. Invalid state: %s" % str(self.plugin_state))

        for hook in self.plugin_hooks:
            try:
                hook.deactivate()
            except Exception as e:
                self.logger.error("Deactivation error in hook %s. Error: %s", hook, e)
        self.plugin_state = Plugin.STATE_DEACTIVATED
        self.notify_state_change(Plugin.STATE_DEACTIVATED)

    def uninstall(self):
        """Uninstalls a plugin.

        Once uninstalled, the plugin will no loger be considered as a part of
        the platform and cannot provide any dependencies.
        """
        if self.plugin_state not in [Plugin.STATE_DEACTIVATED, Plugin.STATE_INSTALLED]:
            raise PluginLifecycleException("Cannot uninstall plugin. Invalid state: %s" % str(self.plugin_state))
        self.plugin_state = Plugin.STATE_UNINSTALLED
        self.notify_state_change(Plugin.STATE_UNINSTALLED)

    def dispose(self):
        """Disposes a plugin.

        When disposing a plugin, the references to the plugin hooks (if any)
        will be deleted so they would be garbadge-collected. Also the references
        to the plugin metadata will be deleted. Once disposed, the plugin cannot
        be re-installed or reused in any way - it awaits final destruction.
        """
        if self.plugin_state is not Plugin.STATE_UNINSTALLED:
            raise PluginLifecycleException("Cannot dispose plugin. Invalid state: %s" % str(self.plugin_state))
        self.plugin_state = Plugin.STATE_DISPOSED
        self.plugin_hooks = None
        self.dispose_dependencies()
        self.plugin = None

    def notify_state_change(self, state):
        """Notifies the plugin hooks if a change in the state of the plugin
        occurs.
        """
        for hook in self.plugin_hooks:
            try:
                hook.on_state_change(state)
            except Exception as e:
                self.logger.error('Error on state change in hook: %s. Error: %s', hook, e)

    def get_environ(self):
        """Returns the sandbox environment of the plugin.

        Once a plugin is created, all of its hooks live in a sandboxed
        environment. This means that the access to other modules (outside the
        plugin native modules) is in the loose sense managed (or in the strctest
        sense constrained) and there have access only to a couple of globals.
        This method defines the globals for the plugin hooks instances.

        If inside a plugin, you can make sure that you're running on the termite
        platforum by checking for the global '__platform__' that will be set to
        the value "termite".

        """
        return {'__platform__': 'termite'}

    def state(self):
        """Returns the current state of the plugin.
        """
        if self.plugin:
            return self.plugin.state
        return None

    def __str__(self):
        return 'PluginContainer {%s, %s (%s)}' % (self.plugin_id, self.version, self.plugin_ref)


class Platform:
    """Represents a single plugins platform.

    A platform manages a set of plugins. It manages the plugins life cycle (
    installation, activation, uninstallation, deactivation, disposal), manages
    the plugins sandboxes - access to specific resources and global shared
    state, manages the plugins access to other plugins packages and modules and
    also manages the plugin dependencies.

    This type is the main entry point for creating and managing the plugins
    system. It provides interface for starting and shutting down the system
    (platform) and for inducing a certaing system-wide state change such as
    installing all plugins, deactivating all plugins and so on.

    The platform delegates the actual plugin life-cycle management to a plugin
    manager (see termite.platform.PluginManager).
    The resource management is delegated to a resource loader
    (see termite.resources.ResourceLoader).
    The access to exposed packages and modules of a plugin is provided and
    managed by a special loader-finder object (see
    termite.loader.PlatformPluginsFinder).


    Configuration

    The platform is initiated with a configuration ojbect. The following are
    some of the most important configuration properties:
        * Section "platform":
            * plugins-dir - a list of directiories that contain plugins. The
            directories names should be separated by comma (,).
            * restricted-modules - a list of restricted python modules. These
            modules will not be available to any plugin on the platform. This
            is a comma (,) separated list of modules names.


    Typical usage

    Typically you want to create an instance of the Platform to manage your
    plugins. In most cases youll need only one instance of the platform per
    application. The creation of a platform object may look like this:
    
    .. code-block:: python
        
        configuration = ConfigParser()
        configuration.read('platform.ini')

        platform = Platform(configuration)

        platform.start()

    All of the plugins are isolated to this platform instance. Each plugin lives
    in a sandboxed space with its own globals/locals ultimately managed by the
    platform instance. Only a few global object will be shared between the
    plugins - for example some modules of the underlying Python path may be
    shared (even between different platform instances if they run in the same
    interpreter).

    """
    STATE_INITIALIZING = 'initializing'
    STATE_ACTIVE = 'active'
    STATE_SHUTTING_DOWN = 'shutting-down'

    def __init__(self, config):
        self.log = logging.getLogger('termite.platform.Platform')
        self.log.info("Termite Platform %s initializing", metadata.version)
        self.config = config
        self.resource_loader = self.create_resource_loader()
        self.plugins_finder = self.create_plugin_finder()
        self.plugins_manager = PluginManager(self.resource_loader, self.plugins_finder)
        self.state = Platform.STATE_INITIALIZING

        # the init was successful
        self.success_init()

    def start(self):
        """Starts the plugin platform.

        The startup process of the platform can be summed up in the following
        steps:
            1. The platform locates the plugins from the plugin directories. The
            plugins may be in different formats (as exploded directory, as some
            kind of archive).
            2. The platform loads the plugins. This means that each plugin
            content is loaded (at least partially) and the metadata is obtained
            (usually the plugin manifest file is read).
            3. The platform installs the plugins. This step checks for plugin
            dependecies. Usually a dependency graph is created and an order of
            installtion is established.
            4. The platform activates the installed plugins.
        """
        # locate all plugins
        # load all plugins
        # install all plugins
        # activate all plugins
        self.log.debug('Platform starting')
        self.load_all_plugins()
        self.install_all_plugins()
        self.activate_all_plugins()
        self.log.info('Platform started')

    def shutdown(self):
        """Shuts down the platform and all plugins managed by it.

        Performs basically the reverse operation of the "start" method. The
        shut down of the platform follow these steps:
            1. Deactivates all the plugins. All active plugins will be notified
            to deactivate and perform theirs deactivation procedure. Waits for
            all plugins to finish the deactivation.
            2. Uninstalls all installed plugins. This frees up the resources and
            destroys the dependency graph.
            3. Destroys all plugins. This releases the resources taken up by
            the plugin loading process.
            4. Performs garbagde collection on any still allocated resources
            before shutting down completely.
        """
        self.log.info('Platform shutting down...')
        self.deactivate_all_plugins()
        self.uninstall_all_plugins()
        self.destroy_all_plugins()
        self.plugins_manager.gc()
        self.log.info('Platform shutdown complete.')

    # helper methods

    def load_all_plugins(self):
        """Scans the plugin directories for plugins and loads the plugins.

        Scans each location for plugins and extracts the plugins references from
        each location. Each plugin reference is then registered with the
        PluginManager which performs the actual loading of the plugin by its
        reference.
        """
        locations = self.config.get('platform', 'plugins-dir', fallback='').split(',') or []
        self.log.info('Loading plugins from these locations: %s' % locations)
        all_refs = []
        for location in locations:
            all_refs = all_refs + plugin_references_from_location(location)
        self.log.info('%d plugins' % len(all_refs))
        for ref in all_refs:
            self.plugins_manager.add_plugin(ref)
        self.log.info('Plugins loaded')

    def install_all_plugins(self):
        """Installs all loaded plugins onto the platform.

        Delegates the actual installation to the PluginManager.
        """
        self.log.debug('Installing all plugins...')
        self.plugins_manager.install_all_plugins()
        self.log.info('All plugins installed')

    def activate_all_plugins(self):
        self.log.debug('Activating all plugins...')
        for plugin_container in self.plugins_manager.get_all_plugins():
            self.log.info('Activating [%s - version %s]' % (plugin_container.plugin_id, plugin_container.version))
            try:
                self.plugins_manager.activate_plugin(plugin_container.plugin_id)
            except Exception:
                self.log.exception('Failed to activate plugin: [%s - version %s]' % (plugin_container.plugin_id,
                                                                                     plugin_container.version))
                self.plugins_manager.deactivate_plugin(plugin_container.plugin_id)
        self.log.info('Plugins activated')

    def deactivate_all_plugins(self):
        self.log.debug('Deactivating all plugins...')
        for plugin_container in self.plugins_manager.get_all_plugins():
            if plugin_container.plugin_state is Plugin.STATE_ACTIVE:
                self.log.debug('Deactivating [%s - version %s]' % (plugin_container.plugin_id,
                                                                   plugin_container.version))
                try:
                    self.plugins_manager.deactivate_plugin(plugin_container.plugin_id)
                    self.log.info('Deactivated [%s - version %s]' % (plugin_container.plugin_id,
                                                                     plugin_container.version))
                except Exception:
                    self.log.exception('Failed to deactivate plugin %s' % plugin_container)
        self.log.info('All Plugins deactivated')

    def uninstall_all_plugins(self):
        self.log.debug('Uninstalling all plugins...')
        for plugin_container in self.plugins_manager.get_all_plugins():
            if plugin_container.plugin_state is Plugin.STATE_INSTALLED or \
               plugin_container.plugin_state is Plugin.STATE_DEACTIVATED:
                self.log.debug('Uninstalling [%s - version %s]' % (plugin_container.plugin_id,
                                                                   plugin_container.version))
                try:
                    self.plugins_manager.uninstall_plugin(plugin_container.plugin_id)
                    self.log.info('Uninstalled [%s - version %s]' % (plugin_container.plugin_id,
                                                                     plugin_container.version))
                except Exception:
                    self.log.exception('Failed to uninstall plugin %s' % plugin_container)
        self.log.info('All Plugins uninstalled')

    def destroy_all_plugins(self):
        self.log.debug('Disposing all plugins...')
        for plugin_container in self.plugins_manager.get_all_plugins():
            if plugin_container.plugin_state is Plugin.STATE_UNINSTALLED:
                self.log.debug('Disposing [%s - version %s]' % (plugin_container.plugin_id,
                                                                plugin_container.version))
                try:
                    self.plugins_manager.deactivate_plugin(plugin_container.plugin_id)
                    self.log.info('Disposed [%s - version %s]' % (plugin_container.plugin_id,
                                                                  plugin_container.version))
                except Exception:
                    self.log.exception('Failed to dispose plugin %s' % plugin_container)
        self.log.info('All Plugins disposed')

    def create_resource_loader(self):
        """Creates new instance of the resource loader capable of loading
        "plugin" and "class" resources type.

        This method may be overriden in a subclass if a special or extended
        implementation of the ResoruceLoader is needed.
        """
        resource_loader = BaseResourceLoader()
        plugin_handler = PluginLoaderHandler(resource_loader)
        class_handler = ClassProtocolHandler(resource_loader)
        resource_loader.add_handler('plugin', plugin_handler)
        resource_loader.add_handler('class', class_handler)
        return resource_loader

    def create_plugin_finder(self):
        """Creates new instance of the plugins finder-loader object.

        This method is an extension point so it can be overriden in a
        subimplementation to provide different implementation of the finder
        object. The return type is expected to be compatible with object of type
        termite.loader.BaseFinder.
        """
        pf = PlatformPluginsFinder(self.get_restricted_modules_list())
        return pf

    def get_restricted_modules_list(self):
        """Returns a list of modules to which the access from the plugins will
        be restricted.

        Currently read from configuration - section `platform`, property
        `restricted-modules`.
        """
        return self.config.get('platform', 'restricted-modules', fallback='').split(',') or []

    def success_init(self):
        """Called when the platform was successfully initialzed.

        Currently registers the global finder object to the system path.
        """
        register_finder(self.plugins_finder)
        self.log.info('Registered path finder: %s' % self.plugins_finder)


class PluginManager:
    """Manages the plugins life-cycle.

    The actual loading of the plugin resources is delegated to a ResoruceLoader.

    The dependency tracking and management is delegated to a
    PluginDependenciesManager.

    The plugin manager keeps track of the plugins, manages with the
    PluginContainers of the plugins and provides a facade for managing the
    life-cycle of each plugin independently or in a bulk.
    """
    def __init__(self, resource_loader, plugin_finder):
        self.log = logging.getLogger('termite.platform.PluginManager')
        self.resource_loader = resource_loader
        self.dependencies_manager = PluginDependenciesManager()
        self.plugin_finder = plugin_finder
        self.plugins_by_ref = {}
        self.plugins_by_id = {}
        self.all_exports = {}
        self.all_requires = {}
        self.dependencies_built = False

    def add_plugin(self, plugin_ref):
        """Registers new plugin with the plugin manager by the plugin reference.

        A new PluginContainer will be created for the plugin reference. If the
        plugin has already be loaded and is managed, the call to this method
        will trigger a reload of the plugin.
        If the plugin was not previously loaded and is not managed, it will be
        registered for management.
        """
        if self.plugins_by_ref.get(plugin_ref):
            raise Exception('Plugin with reference %s already added' % plugin_ref)
        pc = PluginContainer(plugin_ref, self.resource_loader, self)
        pc.load()
        if self.plugins_by_id.get(pc.plugin_id):
            self.reload_plugin(pc.plugin_id, pc)
        else:
            self.plugins_by_ref[plugin_ref] = pc
            self.plugins_by_id[pc.plugin_id] = pc
            self.__build_dependecies__(pc)

    def __load_dependencies__(self, pc):
        """Loads the dependcies for the wrapped plugin using the dependecies
        manager.
        """
        dm = self.dependencies_manager
        dm.dependency(pc.plugin_id)
        dm.add_provider(pc.plugin_id, pc.manifest.version, pc)
        # add all requires as dependencies
        for rq in pc.manifest.requires:
            req_dep = dm.dependency(pc.plugin_id)
            dm.require(pc.plugin_id, rq.name, rq.version_range[0], rq.version_range[1])

        # add all exports as providers as well
        for exp in pc.manifest.exports:
            xdp = dm.dependency(exp.name)
            dm.add_provider(xdp.name, exp.version, pc)


    def reload_plugin(self, plugin_id, plugin_container):
        """Reloads a plugin that is already registered and managed by this
        plugin manager.

        During the reload process, first the plugin dependencies will be cleared
        and the all the dependencies will be build and reloaded again.
        """
        old_plugin = self.plugins_by_id[plugin_id]
        del self.plugins_by_id[plugin_id]
        del self.plugins_by_ref[old_plugin.plugin_ref]
        if self.dependencies_built:
            self.__cleanup_dependencies__(old_plugin)
        self.__build_dependecies__(plugin_container)

    def install_plugin(self, plugin_id):
        """Installs a plugin onto the platform.

        plugin_id is the ID of the plugin to be installed. Note that the plugin
        must be loaded and initialzed before installing.

        During insallation, the declared dependecies will be checked for
        availability. If not all dependencies are available, then an error will
        be raised.

        The plugin resources will be added to the manmaged Finder object to be
        available across the platform and the plugin state will be changed to
        INSTALLED.
        """
        plugin = self.get_plugin(plugin_id)
        if not self.dependencies_manager.all_dependencies_satisfied(plugin_id):
            raise UnsatisfiedDependencyException('Not all dependencies satisfied for plugin: %s' % plugin_id)
        self.plugin_finder.add_plugin(plugin)
        plugin.install()
        self.__mark_available__(plugin)

    def activate_plugin(self, plugin_id):
        plugin = self.get_plugin(plugin_id)
        plugin.activate()

    def deactivate_plugin(self, plugin_id):
        plugin = self.get_plugin(plugin_id)
        if plugin.plugin_state is Plugin.STATE_ACTIVE:
            plugin.deactivate()

    def uninstall_plugin(self, plugin_id):
        plugin = self.get_plugin(plugin_id)
        plugin.uninstall()

    def gc(self):
        pass

    def install_all_plugins(self):
        self.log.debug('Installing all plugins...')
        install_order_deps = self.dependencies_manager.reverese_dependency_order()
        prov_set = set()
        for pd in install_order_deps:
            for version, providers in pd.providers.items():
                for provider in providers:
                    prov_set.add(provider)
        self.log.info('Installing plugins in the following order: %s' % [p.plugin_id for p in prov_set])
        for pc in prov_set:
            self.log.info('Installing plugin: %s' % pc.plugin_id)
            self.install_plugin(pc.plugin_id)
        self.log.info('Plugins installed')

    def get_all_plugins(self):
        return [pr for p, pr in self.plugins_by_id.items()]

    def get_plugin(self, plugin_id):
        plugin = self.plugins_by_id.get(plugin_id)
        if not plugin:
            raise Exception('Plugin with id %s is not registered' % plugin_id)
        return plugin

    def __build_dependecies__(self, plugin_container):
        self.__load_dependencies__(plugin_container)


    def build_dependencies(self):
        # load all exports
        for plugin_id, pc in self.plugins_by_id.items():
            for export in pc.manifest.exports:
                self.all_exports[export] = pc

        # FIXME: This could not possibly be worse
        for plugin_id, pc in self.plugins_by_id.items():
            self.__build_dependecies__(pc)

    def __cleanup_dependencies__(self, plugin_container):
        for export in plugin_container.manifest.exports:
            if self.all_exports.get(export):
                del self.all_exports[export]
        for imp in plugin_container.requires:
            if self.all_requires.get(imp):
                del self.all_requires[imp]
        self.dependencies_manager.delete_dependency(plugin_container.plugin_id)

    def __locate_plugin_for_import__(self, imp):
        for plugin_id, plugin_container in self.plugins_by_id.items():
            if imp.name == plugin_id and imp.version_in_range(plugin_container.manifest.version):
                return plugin_container
        return None

    def __mark_available__(self, plugin_container):
        # self.dependencies_manager.mark_available(plugin_container.plugin_id)
        #for exp in plugin_container.manifest.exports:
        #    self.dependencies_manager.mark_available(exp.name)
        pass

class PlatformException(Exception):
    pass


class PluginLifecycleException(PlatformException):
    pass


class UnsatisfiedDependencyException(PlatformException):
    pass
