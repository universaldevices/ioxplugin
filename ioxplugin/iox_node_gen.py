import ast, astor, json, os
from pathlib import Path
from .nodedef import NodeDefDetails, NodeProperties
from .commands import CommandDetails, CommandParam
from .log import PLUGIN_LOGGER
from .validator import getValidName
from ioxplugin import ast_util 
from .uom import UOMs
from .editor import Editors
from .iox_controller_template import CONTROLLER_TEMPLATE_BODY, CONTROLLER_TEMPLATE_HEADER
IMPL_DIVIDER_AST='########WARNING: DO NOT MODIFY THIS LINE!!! NOTHING BELOW IS REGENERATED!#########'
IMPL_DIVIDER=f'"""{IMPL_DIVIDER_AST}"""'


class IoXImplCommand():
    """
        Simple class that holds names and args for implementation commands
    """

    def __init__(self, name, args):
        self.name=name.replace('__','')
        self.args=args

    def dump(self):
        try:
            arg_list=[]
            if 'query' not in self.name:
                for argv in self.args.values():
                    arg_list.append(argv.replace('_','').lower()) 
            return ast_util.create_impl_command(self.name, arg_list)
        except Exception as ex:
            pass

class IoXNodeGen():
    def __init__(self, nodedef:NodeDefDetails, path:str):
        if nodedef == None or path == None:
            PLUGIN_LOGGER.critical("need node def and the path to save the python file")
            raise Exception ("need node def and the path to save the python file")

        self.nodedef = nodedef
        self.path = path
        self.impl_commands=[]

 
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
            if len(editor.extendedEditors) > 0:
                for ed in editor.extendedEditors:
                    out.append(ast_util.astCommandParamAssignment(f'{param.id}.uom{ed.uom}', param.id))

            impl_args[param.getValidFunctionBodyName()]=param.id
            if is_property:
                body = ast_util.astPHSetPropertyFunc(command_name.replace('__set','update'), param.id)
                for stmt in body:
                    out.append(stmt)
                break

        #out.append(ast_util.astReturnBoolean(True))
        if not is_property:
            body = ast_util.astPHProcessCommandFunc(command_name, impl_args)
            if body:
                for stmt in body:
                    out.append(stmt)

        self.impl_commands.append(IoXImplCommand(command_name,impl_args))

        error.append(ast_util.astLogger("error", "failed parsing parameters ... "))
        error.append(ast_util.astReturnBoolean(False))

        return ast_util.astTryExcept(out, error)

    def create(self, children):
        file_path=f'{self.path}/{self.nodedef.getPythonFileName()}'

        implementation = self.__get_implementation(file_path, IMPL_DIVIDER) 
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
            PLUGIN_LOGGER.critical(str(ex))
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
            PLUGIN_LOGGER.critical(str(ex))
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

        #create update and get methods
        query_commands=[]

        get_uom = ast.FunctionDef(
            name='getUOM',
            args=ast.arguments(
                args=[
                    ast.arg(arg='self', annotation=None),
                    ast.arg(arg='driver', annotation=ast.Name(id='str', ctx=ast.Load()))
                ],
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=[]
            ),
            body=[
                ast.Try(
                    body=[
                        ast.For(
                            target=ast.Name(id='driver_def', ctx=ast.Store()),
                            iter=ast.Attribute(
                                value=ast.Name(id='self', ctx=ast.Load()),
                                attr='drivers',
                                ctx=ast.Load()
                            ),
                            body=[
                                ast.If(
                                    test=ast.Compare(
                                        left=ast.Subscript(
                                            value=ast.Name(id='driver_def', ctx=ast.Load()),
                                            slice=ast.Index(value=ast.Str(s='driver')),
                                            ctx=ast.Load()
                                        ),
                                        ops=[ast.Eq()],
                                        comparators=[ast.Name(id='driver', ctx=ast.Load())]
                                    ),
                                    body=[
                                        ast.Return(
                                            value=ast.Subscript(
                                                value=ast.Name(id='driver_def', ctx=ast.Load()),
                                                slice=ast.Index(value=ast.Str(s='uom')),
                                                ctx=ast.Load()
                                            )
                                        )
                                    ],
                                    orelse=[]
                                )
                            ],
                            orelse=[]
                        ),
                        ast.Return(value=ast.NameConstant(value=None))
                    ],
                    handlers=[
                        ast.ExceptHandler(
                            type=ast.Name(id='Exception', ctx=ast.Load()),
                            name='ex',
                            body=[ast.Return(value=ast.NameConstant(value=None))]
                        )
                    ],
                    orelse=[],
                    finalbody=[]
                )
            ],
            decorator_list=[],
            returns=None
        )


        class_def.body.append(get_uom)

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
                        ast.Name(id='force', ctx=ast.Load()),         # Whether or not to force update/boolean
                        ast.Name(id='text', ctx=ast.Load()),          # Freeform text 
                    ],
                    keywords=[],
                    decorator_list=[]
                )
            return_stmt = ast.Return( value=set_driver_call)  # Return the result of update 
            method = ast.FunctionDef(
            name=f"update{getValidName(driver['name'])}",
            args=ast.arguments(
                args=[ast.arg(arg='self'), ast.arg(arg='value'), ast.arg(arg='force', annotation=ast.Name(id='bool', ctx=ast.Load())), ast.arg(arg='text', annotation=ast.Name(id='str', ctx=ast.Load))],
                defaults=[
                          ast.Constant(value=None),  # Default value for 'force'
                          ast.Constant(value=None)  # Default value for 'text'

                ],
                kwonlyargs=[], 
                kw_defaults=[], 
                vararg=None, kwarg=None
            ),
            body=[
               # ast_util.astComment(f"Use this method to update {getValidName(driver['name'])} in IoX"),
                return_stmt
            ],
            keywords=[],
            decorator_list=[]
            )

            if not self.nodedef.isController:
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
            self.impl_commands.append(IoXImplCommand(command_name,[driver['driver']]))
            query_commands.append(command_name)

            #if not isinstance(body, list):
            #    body = [body]
#
            #return_stmt = ast.Return(value=query_driver_call)  # Return the result of update 
#            method = ast.FunctionDef(
#            name=command_name,
#            args=ast.arguments(
#                args=[ast.arg(arg='self')],
#                defaults=[],
#                kwonlyargs=[], kw_defaults=[], vararg=None, kwarg=None
#            ),
#            body=body,
#            keywords=[],
#            decorator_list=[]
#            )
#            if not self.nodedef.isController:
#                class_def.body.append(method)

        #now make the commands
        for command in commands:
            cmd = self.nodedef.commands.acceptCommands[command['id']]
            pass_stmt = ast.Pass()
            command_name=f"__{getValidName(command['name'],False)}"
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
                        values=[ast.Name(id=f"__{getValidName(command['name'],False)}", ctx=ast.Load()) for command in commands]
                    ) 
            )
            class_def.body.append(commands_list)
            class_def.body.append(ast_util.astComment('    '))
            if len (query_commands) > 0 and not self.nodedef.isController:
                class_def.body.append(ast_util.astQueryAllMethod(query_commands)) 

            if not implementation:
                class_def.body.append(ast_util.astComment('    '))
                class_def.body.append(ast_util.astComment(IMPL_DIVIDER_AST))
                for impl_command in self.impl_commands:
                    class_def.body.append(impl_command.dump())



        with open(file_path, 'a') as file:
            python_code = astor.to_source(class_def)
            file.write(python_code)
            if self.nodedef.isController:
                if implementation:
                    head,_ = self.__get_implementation_from_string(CONTROLLER_TEMPLATE_BODY,IMPL_DIVIDER)
                    if (head):
                        file.write('\n    ')
                        file.write (head)
                else:
                    file.write(CONTROLLER_TEMPLATE_BODY)
            
            if implementation:
                file.write('\n    ')
                file.write(implementation)

        return class_def

    def __get_implementation(self, file_path, delimiter):
        if not Path(file_path).is_file():
            return None

        with open(file_path, 'r') as file:
            content = file.read()
            before, after = self.__get_implementation_from_string(content, delimiter)
            return after

    def __get_implementation_from_string(self, content, delimiter):
        delimiter_pos = content.find(delimiter)
        if delimiter_pos != -1:
            before = content[:delimiter_pos].strip()
            after = content[delimiter_pos:].strip()  # Include the delimiter
            return before,after
        else:
            return None

    