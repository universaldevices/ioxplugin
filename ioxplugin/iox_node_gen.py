import ast, astor
from .nodedef import NodeDefDetails, NodeProperties
from .commands import CommandDetails, CommandParam
from .log import LOGGER
from .validator import getValidName
from ioxplugin import ast_util 
from .uom import UOMs
from .editor import Editors
from .iox_controller_template import CONTROLLER_TEMPLATE_BODY, CONTROLLER_TEMPLATE_HEADER

class IoXNodeGen():
    def __init__(self, nodedef:NodeDefDetails, path:str):
        if nodedef == None or path == None:
            LOGGER.critical("need node def and the path to save the python file")
            raise Exception ("need node def and the path to save the python file")

        self.nodedef = nodedef
        self.path = path
 
    def create_command_body(self, command:CommandDetails, command_name):
        if command == None:
            return None
        
  #      if not command.hasParams() and self.nodedef.isController:
  #          if command_name == "Query" and command.id == "query":
  #              return ast_util.astQueryAllControllerCommand()
  #          if command_name == "Discover" and command.id == "discover":
  #              return ast_util.astDiscoverControllerCommand()
        
        out = []
        error = []
        impl_args ={}

        added_jparams=False
        is_property=command.init_prop != None

        params = command.getParams()
        for p in params:
            param = params[p] 
            editor = Editors.getEditors().editors[param.editor.getEditorId()]
            #if UOMs.isIndex(editor.uom):
            #    out.append(ast_util.astIndexAssignment(param.name.replace(' ','_') if param.name else param.id, param.id, 'command'))
            #else:
            if not added_jparams:
                stmts = ast_util.astCommandQueryParams('command')
                for stmt in stmts:
                    out.append(stmt)
                added_jparams=True
            
            out.append(ast_util.astCommandParamAssignment(f'{param.id}.uom{editor.uom}', param.id))
            impl_args[param.name if param.name else param.id]=param.id
            if is_property:
                body = ast_util.astPHSetPropertyFunc(command_name.replace('set','update'), param.id)
                for stmt in body:
                    out.append(stmt)
                break

        #out.append(ast_util.astReturnBoolean(True))
        if not is_property:
            body = ast_util.astPHProcessCommandFunc(command_name, impl_args)
            if body:
                for stmt in body:
                    out.append(stmt)

        error.append(ast_util.astLogger("error", "failed parsing parameters ... "))
        error.append(ast_util.astReturnBoolean(False))

        return ast_util.astTryExcept(out, error)

    def create(self, children):
        file_path=f'{self.path}/{self.nodedef.getPythonFileName()}'
        with open(file_path, 'w') as file:
            if not self.nodedef.isController:
                imports = ast_util.astCreateImports()
                python_code = astor.to_source(imports)
                file.write(python_code)
                global_defs = ast_util.astCreateGlobals()
                for global_def in global_defs:
                    python_code = astor.to_source(global_def)
                    file.write(python_code) 
            else:
                file.write(CONTROLLER_TEMPLATE_HEADER)    
                for child in children:
                    import_stmt = ast_util.astCreateImportFrom(child['node_class'], child['node_class'])
                    python_code = astor.to_source(import_stmt)
                    file.write(python_code) 

        # Create the class for the node 
        class_def = ast.ClassDef(
            name=f'{self.nodedef.getPythonClassName()}',
            bases=[ast.Attribute(value=ast.Name(id='udi_interface', ctx=ast.Load()), attr='Node', ctx=ast.Load())],
            keywords=[],
            body=[],
            decorator_list=[]
        )

        # Add class-level attributes
        class_def.body.append(ast.Assign(
            targets=[ast.Name(id='id', ctx=ast.Store())],
            value=ast.Str(s=f"{self.nodedef.id}")
        ))

        try:
            drivers = self.nodedef.properties.getPG3Drivers()
        except Exception as ex:
            LOGGER.critical(str(ex))
            raise

        class_def.body.append(ast_util.astComment('This is a list of properties that were defined in the nodedef'))

        # Add the drivers list
        drivers_list = ast.Assign(
            targets=[ast.Name(id='drivers', ctx=ast.Store())],
            value=ast.List(elts=[
                    ast.Dict(
                        keys=[ast.Str(s='driver'), ast.Str(s='value'), ast.Str(s='uom'), ast.Str(s='name')],
                        values=[ast.Str(s=driver['driver']), ast.Str(s=driver['value']), ast.Num(n=driver['uom']), ast.Str(s=driver['name'])]
                    ) for driver in drivers
            ], ctx=ast.Load())
        )

        class_def.body.append(drivers_list)

        try:
            commands = self.nodedef.getPG3Commands()
        except Exception as ex:
            LOGGER.critical(str(ex))
            raise
        
        if self.nodedef.isController:
            children_list = ast.Assign(
                targets=[ast.Name(id='children', ctx=ast.Store())],
                value=ast.List(elts=[
                    ast.Dict(
                        keys=[ast.Str(s='node_class'), ast.Str(s='id'), ast.Str(s='name'), ast.Str(s='parent')],
                        values=[ast.Str(s=child['node_class']), ast.Str(s=child['id']), ast.Str(s=child['name']), ast.Str(s=child['parent'])]
                    ) for child in children
                ], ctx=ast.Load())
            )
            class_def.body.append(children_list)


        defaults=[self.nodedef.parent if self.nodedef.parent else self.nodedef.id,  self.nodedef.id,  self.nodedef.name]
        class_def.body.append(ast_util.astAddClassInit(self.nodedef.isController, defaults, None))
        if self.nodedef.isController:
            pass
            #set protocol handler
            #class_def.body.append(ast_util.astSetPluginFunc())
            #class_def.body.append(ast_util.astConfigFunc())
            #class_def.body.append(ast_util.astStartFunc())
            #class_def.body.append(ast_util.astStopFunc())
            #class_def.body.append(ast_util.astPollFunc())
            #class_def.body.append(ast_util.astAddAllNodesFunc())
            #class_def.body.append(ast_util.astAddNodeFunc())
        else:
            #set protocol handler
            class_def.body.append(ast_util.astSetPluginFunc())

        #create update and get methods
        query_commands=[]


        for driver in drivers:
            set_driver_call=ast.Call(
                        func=ast.Attribute(
                        value=ast.Name(id='self', ctx=ast.Load()),  # 'self' object
                        attr='setDriver',  # Method name 'setDriver'
                        ctx=ast.Load()
                    ),
                    args=[
                        ast.Name(id=f"\"{driver['driver']}\"", ctx=ast.Load()),  # First, driver id
                        ast.Name(id='value', ctx=ast.Load()),        # Second, value
                        ast.Name(id=f"{driver['uom']}", ctx=ast.Load()) ,    # Third uom
                        ast.Name(id='force', ctx=ast.Load())          # Whether or not to force update/boolean
                    ],
                    keywords=[],
                    decorator_list=[]
                )
            return_stmt = ast.Return( value=set_driver_call)  # Return the result of update 
            method = ast.FunctionDef(
            name=f"update{getValidName(driver['name'])}",
            args=ast.arguments(
                args=[ast.arg(arg='self'), ast.arg(arg='value'), ast.arg(arg='force', annotation=ast.Name(id='bool', ctx=ast.Load()))],
                defaults=[],
                kwonlyargs=[], kw_defaults=[], vararg=None, kwarg=None
            ),
            body=[
                return_stmt
            ],
            keywords=[],
            decorator_list=[]
            )

            if not self.nodedef.isController:
                class_def.body.append(ast_util.astComment(f"Use this method to update {getValidName(driver['name'])} in IoX"))
                class_def.body.append(method)

            ## Now getDriver
            get_driver_call=ast.Call(
                        func=ast.Attribute(
                        value=ast.Name(id='self', ctx=ast.Load()),  # 'self' object
                        attr='getDriver',  # Method name 'getDriver'
                        ctx=ast.Load()
                    ),
                    args=[
                        ast.Name(id=f"\"{driver['driver']}\"", ctx=ast.Load())  # First, driver id
                    ],
                    keywords=[],
                    decorator_list=[]
                )
            return_stmt = ast.Return( value=get_driver_call)  # Return the result of update 
            method = ast.FunctionDef(
            name=f"get{getValidName(driver['name'])}",
            args=ast.arguments(
                args=[ast.arg(arg='self')],
                defaults=[],
                kwonlyargs=[], kw_defaults=[], vararg=None, kwarg=None
            ),
            body=[
                return_stmt
            ],
            keywords=[],
            decorator_list=[]
            )
            if not self.nodedef.isController:
                class_def.body.append(method)

            ## Now queryriver
            command_name=f"query{getValidName(driver['name'])}"
            update_name=f"update{getValidName(driver['name'])}"
            query_commands.append(command_name)
            body = ast_util.astPHQueryPropertyFunc(update_name, driver['driver'])

            if not isinstance(body, list):
                body = [body]

            #return_stmt = ast.Return(value=query_driver_call)  # Return the result of update 
            method = ast.FunctionDef(
            name=command_name,
            args=ast.arguments(
                args=[ast.arg(arg='self')],
                defaults=[],
                kwonlyargs=[], kw_defaults=[], vararg=None, kwarg=None
            ),
            body=body,
            keywords=[],
            decorator_list=[]
            )
            if not self.nodedef.isController:
                class_def.body.append(method)

        if len (query_commands) > 0 and not self.nodedef.isController:
            class_def.body.append(ast_util.astQueryAllMethod(query_commands)) 

        #now make the commands
        for command in commands:
            cmd = self.nodedef.commands.acceptCommands[command['id']]
            pass_stmt = ast.Pass()
            command_name=getValidName(command['name'],False)
            body = self.create_command_body(cmd, command_name)
            if not isinstance(body, list):
                body = [body]
            method = ast.FunctionDef(
                name=command_name,
                args=ast.arguments(
                    args=[ast.arg(arg='self'), ast.arg(arg='command')],
                    defaults=[],
                    kwonlyargs=[], kw_defaults=[], vararg=None, kwarg=None
                ),
                body=body,
                #body=[
                #     self.create_command_body(cmd, command_name)
                #],
                keywords=[],
                decorator_list=[]
            )
            if not self.nodedef.isController:
                class_def.body.append(method)

        # Print the AST dump to verify
        #print(ast.dump(class_def, indent=4))
        if not self.nodedef.isController:
            class_def.body.append(ast_util.astComment('This is a list of commands that were defined in the nodedef'))
            # Add the drivers list
            commands_list = ast.Assign(
            targets=[ast.Name(id='commands', ctx=ast.Store())],
            value= ast.Dict(
                        keys=[ast.Str(s=f"{command['id']}") for command in commands],
                        values=[ast.Name(id=f"{getValidName(command['name'],False)}", ctx=ast.Load()) for command in commands]
                    ) 
            )
            class_def.body.append(commands_list)

        with open(file_path, 'a') as file:
            python_code = astor.to_source(class_def)
            file.write(python_code)
            if self.nodedef.isController:
                file.write(CONTROLLER_TEMPLATE_BODY)

        return class_def

    