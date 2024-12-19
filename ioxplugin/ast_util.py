import ast


def astComment(comment):
    return ast.Expr(value=ast.Constant(value=comment))

def astReturnBoolean(val:bool):
    # Create an AST node for 'return True'
    return ast.Return(
        value=ast.Constant(value=val)  # Using ast.Constant for Python 3.8 and later
    )

def astCreateImports():
    import_node = ast.Import(
        names=[
                ast.alias(name='udi_interface', asname=None),
                ast.alias(name='os', asname=None),
                ast.alias(name='sys', asname=None),
                ast.alias(name='json', asname=None),
                ast.alias(name='time', asname=None),
            ]
    )
    return import_node 

def astCreateImport(import_name):
    return ast.Import(
        names=[
                ast.alias(name=import_name, asname=None)
            ]
    )

def astCreateImportFrom(module_name, class_name):
    # Creating an AST node for 'from udi_interface import crap'
    return ast.ImportFrom(
        module=module_name,
        names=[ast.alias(name=class_name, asname=None)],
        level=0
    )

def astCreateGlobals(logger_only=False):
    # AST node for 'LOGGER = udi_interface.LOGGER'
    assign_LOGGER = ast.Assign(
    targets=[ast.Name(id='LOGGER', ctx=ast.Store())],
    value=ast.Attribute(
            value=ast.Name(id='udi_interface', ctx=ast.Load()),
            attr='LOGGER',
            ctx=ast.Load()
            )
        )

    if logger_only:
        return [assign_LOGGER]

    # AST node for 'Custom = udi_interface.Custom'
    assign_Custom = ast.Assign(
    targets=[ast.Name(id='Custom', ctx=ast.Store())],
    value=ast.Attribute(
            value=ast.Name(id='udi_interface', ctx=ast.Load()),
            attr='Custom',
            ctx=ast.Load()
            )
    )

    return [assign_LOGGER, assign_Custom]


def astIndexAssignment(variable_name, param, command):
    return ast.Assign(
        targets=[ast.Name(id=variable_name, ctx=ast.Store())],  # The variable 'value' to assign to
        value=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id=command, ctx=ast.Load()),  # The dictionary 'command'
                attr='get',  # The 'get' method of dictionary
                ctx=ast.Load()
            ),
            args=[
                ast.Constant(value=param)  # Argument 'param' for the get method
            ],
            keywords=[]  # No keyword arguments
        )
    )

#level: error, info, debug, warning
def astLogger(level, message, add_exception=True):
    # Create an AST node for the LOGGER.error call with an f-string
    t_values=[
                ast.Str(s=message)  # Static part of the string
                #ast.Str(s=message),  # Static part of the string
                #ast.FormattedValue(
                #    value=ast.Attribute(
                #        value=ast.Name(id='self', ctx=ast.Load()),
                #        attr='name',
                #        ctx=ast.Load()
                #    ),
                #    conversion=-1,  # -1 indicates default string conversion
                #    format_spec=None
                #)
            ]

    if add_exception:
        values=[
            ast.Str(s=f"{message} :"),  # Static part of the string
            ast.FormattedValue(
            value=ast.Name(id='ex', ctx=ast.Load()),  # Dynamic part, variable ex
            conversion=-1,  # -1 means no conversion, 115 for str(), 114 for repr(), 97 for ascii()
            format_spec=None  # No specific format
        )
    ]

    logger = ast.Expr(
        value=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='LOGGER', ctx=ast.Load()),  # LOGGER object
                attr=level,  # the level such as error, info, warning, etc. 
                ctx=ast.Load()
            ),
            args=[
                ast.JoinedStr(
                    values=t_values
#[
 #                       ast.Str(s=f"{message} :"),  # Static part of the string
 #                       ast.FormattedValue(
 #                           value=ast.Name(id='ex', ctx=ast.Load()),  # Dynamic part, variable ex
 #                           conversion=-1,  # -1 means no conversion, 115 for str(), 114 for repr(), 97 for ascii()
 #                           format_spec=None  # No specific format
 #                       )
 #                   ]
                )
            ],
            keywords=[]  # No keyword arguments
        )
    )
    return logger



#body and error are arrays of statements
def astTryExcept(body, error):
    # Try-Except block
    try_except = ast.Try(
        body=body,
        handlers=[
            ast.ExceptHandler(
                type=ast.Name(id='Exception', ctx=ast.Load()),
                name=ast.Name(id='ex', ctx=ast.Store()),
                body=error
            )
        ],
        orelse=[],
        finalbody=[]
    )

    return try_except


def astCommandQueryParams(command):
    # Nodes for the try block
    # Assignment: query = str(command['query']).replace("'", "\"")
    query_assign = ast.Assign(
        targets=[ast.Name(id='query', ctx=ast.Store())],
        value=ast.Call(
            func=ast.Attribute(
                value=ast.Call(
                    func=ast.Name(id='str', ctx=ast.Load()),
                    args=[ast.Subscript(
                        value=ast.Name(id=command, ctx=ast.Load()),
                        slice=ast.Index(value=ast.Constant(value='query')),
                        ctx=ast.Load()
                    )],
                    keywords=[]
                ),
                attr='replace',
                ctx=ast.Load()
            ),
            args=[ast.Constant(value="'"), ast.Constant(value='"')],
            keywords=[]
        )
    )

    # Assignment: jparam = json.loads(query)
    jparam_assign = ast.Assign(
        targets=[ast.Name(id='jparam', ctx=ast.Store())],
        value=ast.Call(
            func=ast.Attribute(value=ast.Name(id='json', ctx=ast.Load()), attr='loads', ctx=ast.Load()),
            args=[ast.Name(id='query', ctx=ast.Load())],
            keywords=[]
        )
    )

    return [query_assign, jparam_assign]

#toInt whether or not convert to int
def astCommandParamAssignment(param_uom, val_name, toInt=True):
    # Assignment: val = int(jparam['WCTRL.uom78'])
    if toInt:
        return ast.If( 
            test=ast.Compare(
                left=ast.Constant(value=param_uom),
                ops=[ast.In()],
                comparators=[ast.Name(id='jparam', ctx=ast.Load())]
            ),
            body=[
                ast.Assign(
                targets=[ast.Name(id=val_name, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Name(id='int', ctx=ast.Load()),
                    args=[ast.Subscript(
                        value=ast.Name(id='jparam', ctx=ast.Load()),
                        slice=ast.Index(value=ast.Constant(value=param_uom)),
                        ctx=ast.Load()
                        )],
                        keywords=[]
                    )
                ),
            ],
            orelse=[]
        )
    return ast.If( 
        test=ast.Compare(
            left=ast.Constant(value=param_uom),
            ops=[ast.In()],
            comparators=[ast.Name(id='jparam', ctx=ast.Load())]
        ),
        body=[
            ast.Assign(
            targets=[ast.Name(id=val_name, ctx=ast.Store())],  # Variable 
            value=ast.Subscript(
                value=ast.Name(id='jparam', ctx=ast.Load()),  # The dictionary 'jparam'
                slice=ast.Index(value=ast.Constant(value=param_uom)),  # Key 
                ctx=ast.Load()  # Context for the Subscript
                )
            )
        ],
        orelse=[]
    )

def astInitBody(impl_class_name:str):
    out = [ast.Expr(value=ast.Call(
        func=ast.Attribute(
            value=ast.Call(
                func=ast.Name(id='super', ctx=ast.Load()),
                args=[],
                keywords=[]
            ),
            attr='__init__',
            ctx=ast.Load()
        ),
        args=[
            ast.Name(id='polyglot', ctx=ast.Load()),
            ast.Name(id='controller', ctx=ast.Load()),
            ast.Name(id='address', ctx=ast.Load()),
            ast.Name(id='name', ctx=ast.Load())
        ],
        keywords=[]
    ))]

    if impl_class_name:
          # Create AST node for Impl(self) call
        impl_call_node = ast.Call(
            func=ast.Name(id=impl_class_name, ctx=ast.Load()),
            args=[ast.Name(id='self', ctx=ast.Load())],
        keywords=[]
        )

        inst_name = impl_class_name[0].lower() + impl_class_name[1:]
        # Create AST node for self.impl = Impl(self) assignment
        assign_node = ast.Assign(
            targets=[ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr=inst_name, ctx=ast.Store())],
            value=impl_call_node
        )
        out.append(assign_node)

    #add plugin handler if any.
    ph_node = ast.Assign(
            targets=[
            ast.Attribute(
                value=ast.Name(id='self', ctx=ast.Load()),
                attr='plugin',
                ctx=ast.Store()
                )
            ],
            value=ast.Name(id='plugin', ctx=ast.Load())
        )
    out.append(ph_node)
    return out

def astInitBodyController():
    return [

        ast.Assign(
            targets=[ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='Parameters', ctx=ast.Store())],
            value=ast.Call(
                func=ast.Name(id='Custom', ctx=ast.Load()),
                args=[
                    ast.Name(id='polyglot', ctx=ast.Load()),
                    ast.Constant(value='customparams')
                ],
                keywords=[]
            )
        ),
        #self.poly.addNode(self)
        ast.Expr(value=ast.Call(
            func=ast.Attribute(
                value=ast.Attribute(
                    value=ast.Name(id='self', ctx=ast.Load()),
                    attr='poly',
                    ctx=ast.Load()
                ),
                attr='addNode',
                ctx=ast.Load()
            ),
            args=[ast.Name(id='self', ctx=ast.Load())],
            keywords=[ 
                ast.keyword(
                    arg='conn_status',
                    value=ast.Constant(value='ST')
                )]
        )),
        #Setting oauthService 
        ast.Assign(
            targets=[ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='oauthService', ctx=ast.Store())],
            value=ast.Constant(value=None)
        ),
        # Setting valid_configuration attribute
        #ast.Assign(
        #    targets=[ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='valid_configuration', ctx=ast.Store())],
        #    value=ast.Constant(value=False)
        #),
        # Setting started attribute
        #ast.Assign(
        #    targets=[ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='started', ctx=ast.Store())],
        #    value=ast.Constant(value=False)
        #),
        # Multiple subscribe method calls
        ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()), attr='subscribe', ctx=ast.Load()),
            args=[ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='START', ctx=ast.Load()), ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='__start', ctx=ast.Load()), ast.Name(id='address', ctx=ast.Load())],
            keywords=[]
        )),
        ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()), attr='subscribe', ctx=ast.Load()),
            args=[ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='CUSTOMPARAMS', ctx=ast.Load()), ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='parameterHandler', ctx=ast.Load())],
            keywords=[]
        )),
        ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()), attr='subscribe', ctx=ast.Load()),
            args=[ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='POLL', ctx=ast.Load()), ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='__poll', ctx=ast.Load())],
            keywords=[]
        )),
        ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()), attr='subscribe', ctx=ast.Load()),
            args=[ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='STOP', ctx=ast.Load()), ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='__stop', ctx=ast.Load())],
            keywords=[]
        )),
        ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()), attr='subscribe', ctx=ast.Load()),
            args=[ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='CONFIG', ctx=ast.Load()), ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='__configHandler', ctx=ast.Load())],
            keywords=[]
        )),
        ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()), attr='subscribe', ctx=ast.Load()),
            args=[ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='CONFIGDONE', ctx=ast.Load()), ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='__configDoneHandler', ctx=ast.Load())],
            keywords=[]
        )),
        ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()), attr='subscribe', ctx=ast.Load()),
            args=[ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='ADDNODEDONE', ctx=ast.Load()), ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='__addNodeDoneHandler', ctx=ast.Load())],
            keywords=[]
        )),
        ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()), attr='subscribe', ctx=ast.Load()),
            args=[ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='CUSTOMNS', ctx=ast.Load()), ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='__customNSHandler', ctx=ast.Load())],
            keywords=[]
        )),
#        ast.Expr(value=ast.Call(
#            func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()), attr='subscribe', ctx=ast.Load()),
#            args=[ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='OAUTH', ctx=ast.Load()), ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='oauthHandler', ctx=ast.Load())],
#            keywords=[]
#        )),
        ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()), attr='subscribe', ctx=ast.Load()),
            args=[ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='CUSTOMDATA', ctx=ast.Load()), ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='customDataHandler', ctx=ast.Load())],
            keywords=[]
        )),
        ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()), attr='subscribe', ctx=ast.Load()),
            args=[ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='DISCOVER', ctx=ast.Load()), ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='discover', ctx=ast.Load())],
            keywords=[]
        )),
        ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()), attr='subscribe', ctx=ast.Load()),
            args=[ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='BONJOUR', ctx=ast.Load()), ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='__bonjourHandler', ctx=ast.Load())],
            keywords=[]
        )),
        ast.Assign(
            targets=[
                ast.Attribute(
                    value=ast.Name(id='self', ctx=ast.Load()),
                    attr='configDone',
                    ctx=ast.Store()
                )
            ],
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='threading', ctx=ast.Load()),
                    attr='Condition',
                    ctx=ast.Load()
                ),
                args=[],
                keywords=[]
            )
        ),
        ast.Expr(value=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='self', ctx=ast.Load()),
                attr='__initOAuth',
                ctx=ast.Load()
            ),
            args=[],  # No arguments are passed to the function
            keywords=[]  # No keyword arguments
        )),
        ast.Assign(
            targets=[
                ast.Attribute(
                    value=ast.Name(id='self', ctx=ast.Load()),
                    attr='configDoneAlready',
                    ctx=ast.Store()
                )
            ],
            value=ast.Constant(value=False),
            type_comment=None
        )
    ]   

def astAddImplClassInit():
    # Create AST node for self.node = node assignment
    assign_node = ast.Assign(
        targets=[ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='plugin', ctx=ast.Store())],
        value=ast.Name(id='plugin', ctx=ast.Load())
    )

    # Create AST node for method body
    body_node = [assign_node]
    function_def = ast.FunctionDef(
        name='__init__',
        args=ast.arguments(
            posonlyargs=[],
            args=[
                ast.arg(arg='self'),
                ast.arg(arg='plugin')
            ],
            defaults=[],
            kwonlyargs=[],
            kw_defaults=[],
            vararg=None,
            kwarg=None
        ),
        body=[
            assign_node
        ],
        decorator_list=[],
        returns=None
    )

    return function_def

def astCallImplMethod(impl_instance_name, method_name, args_array):
     # Create AST node for class attribute access
    class_node = ast.Name(id=impl_instance_name, ctx=ast.Load())
    method_node = ast.Attribute(value=class_node, attr=method_name, ctx=ast.Load())

    # Create AST nodes for arguments
    arg_nodes = [ast.Name(id=arg, ctx=ast.Load()) for arg in args_array] if args_array else []

    # Create AST node for function call
    call_node = ast.Call(
        func=method_node,
        args=arg_nodes,
        keywords=[]
    )

    # Create AST node for expression statement
    return ast.Return(value=call_node)

def astAddClassInit(is_controller, defaults_array, impl_class_name):
    init_body = astInitBody(None if is_controller else impl_class_name)
    if (is_controller):
       init_body += astInitBodyController()

    # Function definition with default arguments
    function_def = ast.FunctionDef(
        name='__init__',
        args=ast.arguments(
            posonlyargs=[],
            args=[
                ast.arg(arg='self'),
                ast.arg(arg='polyglot'),
                ast.arg(arg='plugin', annotation=None, type_comment=None),
                ast.arg(arg='controller', annotation=None, type_comment=None),
                ast.arg(arg='address', annotation=None, type_comment=None),
                ast.arg(arg='name', annotation=None, type_comment=None)
            ],
            defaults=[
               ast.Constant(value=d) for d in defaults_array
            ],
            kwonlyargs=[],
            kw_defaults=[],
            vararg=None,
            kwarg=None
        ),
        body=init_body,
        decorator_list=[],
        returns=None
    )

    return function_def

import ast

def astQueryAllMethod(commands):
    if commands == None or len(commands) <= 0:
        return None

    function_def = ast.FunctionDef(
        name='queryAll',
        args=ast.arguments(args=[ ast.arg(arg='self', annotation=None)], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
        body=[],
        decorator_list=[],
        returns=None
    )

    # Add a method call for each query to the function body
    for command in commands:
        method_call = ast.Expr(
        value=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='self', ctx=ast.Load()),
                attr=command,
                ctx=ast.Load()
            ),
            args=[],
            keywords=[]
            )
        )
        function_def.body.append(method_call)
    return function_def


#protocol handler
def astPHSetPropertyFunc(update_method, property):
    set_method=update_method.replace('update','set')
    #command_name=command_name.replace('__','')
    #for arg in args_array:
    #    arg_nodes.append(ast.Name(id=arg, ctx=ast.Load))
    # Create AST node for function call
    return_statement = ast.Return(
            value=ast.Call(
            func=ast.Name(id=f'self.{set_method}', ctx=ast.Load()),
            args= [
                ast.Name(id=property, ctx=ast.Load)
            ],
            keywords=[]
        )
    )
    return [return_statement]

def astPHProcessCommandFunc(command_name, args):

    command_name=command_name.replace('__','')
    #for arg in args_array:
    #    arg_nodes.append(ast.Name(id=arg, ctx=ast.Load))
    # Create AST node for function call
    return_statement = ast.Return(
            value=ast.Call(
            func=ast.Name(id=f'self.{command_name}', ctx=ast.Load()),
            args= [
                ast.Name(id=val, ctx=ast.Load)for key, val in args.items()
            ],
            keywords=[]
        )
    )
    return [return_statement]


def create_impl_command(command_name, args):
    """
    Creates an AST for a Python function with a try/except block.

    Args:
        function_name (str): The name of the imple command to create.
        args (list): A list of argument names

    """
    # Create AST nodes for arguments
    command_args = ast.arguments(
        posonlyargs=[],  # No positional-only arguments
        args=[ast.arg(arg=arg, annotation=None) for arg in args],  # Positional arguments
        vararg=None,  # No *args
        kwonlyargs=[],  # No keyword-only arguments
        kw_defaults=[],  # No defaults for keyword-only args
        defaults=[]  # No default values
    )

    # Create the try/except block
    try_block = ast.Try(
        body=[ast.Return(value=ast.Constant(value=True))],  # return True in try block
        handlers=[
            ast.ExceptHandler(
                type=None,  # Catch all exceptions
                name=None,
                body=[ast.Return(value=ast.Constant(value=False))]  # return False in except block
            )
        ],
        orelse=[],  # No else block
        finalbody=[]  # No finally block
    )

    # Create the FunctionDef node
    function_def = ast.FunctionDef(
        name=command_name,
        args=command_args,
        body=[try_block],
        decorator_list=[],
        returns=None
    )

    return function_def
