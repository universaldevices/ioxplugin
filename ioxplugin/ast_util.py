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
        return ast.Assign(
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
        )
    return ast.Assign(
        targets=[ast.Name(id=val_name, ctx=ast.Store())],  # Variable 
        value=ast.Subscript(
            value=ast.Name(id='jparam', ctx=ast.Load()),  # The dictionary 'jparam'
            slice=ast.Index(value=ast.Constant(value=param_uom)),  # Key 
            ctx=ast.Load()  # Context for the Subscript
        )
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

    #add protocol handler if any.
    ph_node = ast.Assign(
            targets=[
            ast.Attribute(
                value=ast.Name(id='self', ctx=ast.Load()),
                attr='protocolHandler',
                ctx=ast.Store()
                )
            ],
            value=ast.Name(id='protocolHandler', ctx=ast.Load())
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
            args=[ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='START', ctx=ast.Load()), ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='start', ctx=ast.Load())],
            keywords=[]
        )),
        ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()), attr='subscribe', ctx=ast.Load()),
            args=[ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='CUSTOMPARAMS', ctx=ast.Load()), ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='parameterHandler', ctx=ast.Load())],
            keywords=[]
        )),
        ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()), attr='subscribe', ctx=ast.Load()),
            args=[ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='POLL', ctx=ast.Load()), ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poll', ctx=ast.Load())],
            keywords=[]
        )),
        ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()), attr='subscribe', ctx=ast.Load()),
            args=[ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='STOP', ctx=ast.Load()), ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='stop', ctx=ast.Load())],
            keywords=[]
        )),
        ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()), attr='subscribe', ctx=ast.Load()),
            args=[ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='CONFIG', ctx=ast.Load()), ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='configHandler', ctx=ast.Load())],
            keywords=[]
        )),
        ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()), attr='subscribe', ctx=ast.Load()),
            args=[ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='CONFIGDONE', ctx=ast.Load()), ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='configDoneHandler', ctx=ast.Load())],
            keywords=[]
        )),
        ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()), attr='subscribe', ctx=ast.Load()),
            args=[ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='ADDNODEDONE', ctx=ast.Load()), ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='addNodeDoneHandler', ctx=ast.Load())],
            keywords=[]
        )),
        ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()), attr='subscribe', ctx=ast.Load()),
            args=[ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='CUSTOMNS', ctx=ast.Load()), ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='customNSHandler', ctx=ast.Load())],
            keywords=[]
        )),
        ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()), attr='subscribe', ctx=ast.Load()),
            args=[ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='OAUTH', ctx=ast.Load()), ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='oauthHandler', ctx=ast.Load())],
            keywords=[]
        )),
        ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()), attr='subscribe', ctx=ast.Load()),
            args=[ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='CUSTOMDATA', ctx=ast.Load()), ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='customDataHandler', ctx=ast.Load())],
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
                attr='initOAuth',
                ctx=ast.Load()
            ),
            args=[],  # No arguments are passed to the function
            keywords=[]  # No keyword arguments
        ))
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
                ast.arg(arg='protocolHandler', annotation=None, type_comment=None),
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

def astStartFunc():
    log_info = astLogger('info', 'Starting ... ', False)
    function_def = ast.FunctionDef(
        name='start',
        args=ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg='self')],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[]
        ),
        body=[
            # LOGGER.info(f'Starting... ')
            ast.Expr(value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='LOGGER', ctx=ast.Load()),
                    attr='info',
                    ctx=ast.Load()
                ),
                args=[ast.JoinedStr(
                    values=[
                        ast.Constant(value='Starting... ')
                    ]
                )],
                keywords=[]
            )),
            # self.poly.addNode(self)
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
                keywords=[]
            )),
            # self.addAllNodes()
            ast.Expr(value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='self', ctx=ast.Load()),
                    attr='addAllNodes',
                    ctx=ast.Load()
                ),
                args=[],
                keywords=[]
            )),
            # polyglot.updateProfile()
            ast.Expr(value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='self', ctx=ast.Load()),
                    attr='poly.updateProfile',
                    ctx=ast.Load()
                ),
                args=[],
                keywords=[]
            )),
            # self.poly.setCustomParamsDoc()
            ast.Expr(value=ast.Call(
                func=ast.Attribute(
                    value=ast.Attribute(
                        value=ast.Name(id='self', ctx=ast.Load()),
                        attr='poly',
                        ctx=ast.Load()
                    ),
                    attr='setCustomParamsDoc',
                    ctx=ast.Load()
                ),
                args=[],
                keywords=[]
            )),
            # self.poly.ready()
            ast.Expr(value=ast.Call(
                func=ast.Attribute(
                    value=ast.Attribute(
                        value=ast.Name(id='self', ctx=ast.Load()),
                        attr='poly',
                        ctx=ast.Load()
                    ),
                    attr='ready',
                    ctx=ast.Load()
                ),
                args=[],
                keywords=[]
            )),
            # return True
            ast.Return(value=ast.Constant(value=True))
        ],
        decorator_list=[],
        returns=None
    )

    return function_def


import ast

def astStopFunc():
    # Function body: LOGGER.info(f"Stopping {self.name}")
    log_stop = astLogger('info', 'Stopping ... ', False)
    return_true = astReturnBoolean(True)

    #dFunction definition: def stop(self):
    function_def = ast.FunctionDef(
        name='stop',
        args=ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg='self')],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[]
        ),
        body=[log_stop, return_true],
        decorator_list=[],
        returns=None
    )

    return function_def

def astConfigFunc():
    # Function body: LOGGER.info(f"Stopping {self.name}")
    log_stop = astLogger('info', 'Config ... ', False)
    return_true = astReturnBoolean(True)

    #dFunction definition: def stop(self):
    function_def = ast.FunctionDef(
        name='config',
        args=ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg='self')],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[]
        ),
        body=[log_stop, return_true],
        decorator_list=[],
        returns=None
    )

    return function_def

def astPollFunc():
    # LOGGER.info("short poll")
    log_short_poll = astLogger('info', 'Short poll ... ', False)
    log_long_poll = astLogger('info', 'Long poll ... ', False)

    # Elif 'longPoll' in polltype
    elif_long_poll = ast.If(
        test=ast.Compare(
            left=ast.Constant(value='longPoll'),
            ops=[ast.In()],
            comparators=[ast.Name(id='polltype', ctx=ast.Load())]
        ),
        body=[log_long_poll],
        orelse=[]
    )

    # If 'shortPoll' in polltype
    if_short_poll = ast.If(
        test=ast.Compare(
            left=ast.Constant(value='shortPoll'),
            ops=[ast.In()],
            comparators=[ast.Name(id='polltype', ctx=ast.Load())]
        ),
        body=[log_short_poll],
        orelse=[elif_long_poll]  # Elif is represented by an If in the orelse of the first If
    )

    # Function definition: def poll(polltype):
    function_def = ast.FunctionDef(
        name='poll',
        args=ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg='self'), ast.arg(arg='polltype')],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[]
        ),
        body=[if_short_poll],
        decorator_list=[],
        returns=None
    )

    return function_def

def astAddAllNodesFunc(): 
    # Create AST for the function definition
    function_def = ast.FunctionDef(
        name='addAllNodes',
        args=ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg='self')],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[]
        ),
        body=[
            # Assign config from self.poly.getConfig()
            ast.Assign(
                targets=[ast.Name(id='config', ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Attribute(
                            value=ast.Name(id='self', ctx=ast.Load()),
                            attr='poly',
                            ctx=ast.Load()),
                        attr='getConfig',
                        ctx=ast.Load()),
                    args=[],
                    keywords=[]
                )
            ),
            # Conditional to check and reset config if necessary
            ast.If(
                test=ast.BoolOp(
                op=ast.Or(),
                values=[
                    ast.Compare(
                        left=ast.Name(id='config', ctx=ast.Load()),
                        ops=[ast.Is()],
                        comparators=[ast.Constant(value=None)]
                    ),
                    ast.Compare(
                        left=ast.Subscript(
                            value=ast.Name(id='config', ctx=ast.Load()),
                            slice=ast.Index(value=ast.Constant(value='nodes')),
                            ctx=ast.Load()
                        ),
                        ops=[ast.Is()],
                        comparators=[ast.Constant(value=None)]
                    ),
                    ast.Compare(
                        left=ast.Call(
                            func=ast.Name(id='len', ctx=ast.Load()),
                            args=[ast.Subscript(
                                value=ast.Name(id='config', ctx=ast.Load()),
                                slice=ast.Index(value=ast.Constant(value='nodes')),
                                ctx=ast.Load()
                            )],
                            keywords=[]
                        ),
                        ops=[ast.LtE()],
                        comparators=[ast.Constant(value=0)]
                    )
                ]
                ),
                body=[
                    ast.Assign(
                        targets=[ast.Name(id='config', ctx=ast.Store())],
                        value=ast.Dict(keys=[], values=[])
                    ),
                    ast.Assign(
                        targets=[ast.Subscript(
                            value=ast.Name(id='config', ctx=ast.Load()),
                            slice=ast.Index(value=ast.Constant(value='nodes')),
                            ctx=ast.Store()
                        )],
                        value=ast.List(elts=[], ctx=ast.Load())
                    ),
                    ast.For(
                        target=ast.Name(id='child', ctx=ast.Store()),
                        iter=ast.Attribute(
                            value=ast.Name(id='self', ctx=ast.Load()),  # The object being iterated over
                            attr='children',  # The attribute of the object that provides the iterable
                            ctx=ast.Load()),
                        body=[
                            ast.Expr(
                                value=ast.Call(
                                    func=ast.Attribute(
                                        value=ast.Subscript(
                                            value=ast.Name(id='config', ctx=ast.Load()),
                                            slice=ast.Index(value=ast.Constant(value='nodes')),
                                            ctx=ast.Load()
                                        ),
                                        attr='append',
                                        ctx=ast.Load()
                                    ),
                                    args=[ast.Dict(
                                        keys=[
                                            ast.Constant(value='nodeDefId'),
                                            ast.Constant(value='address'),
                                            ast.Constant(value='name'),
                                            ast.Constant(value='primaryNode')
                                        ],
                                        values=[
                                            ast.Subscript(
                                                value=ast.Name(id='child', ctx=ast.Load()),
                                                slice=ast.Index(value=ast.Constant(value='id')),
                                                ctx=ast.Load()
                                            ),
                                            ast.Subscript(
                                                value=ast.Name(id='child', ctx=ast.Load()),
                                                slice=ast.Index(value=ast.Constant(value='node_class')),
                                                ctx=ast.Load()
                                            ),
                                            ast.Subscript(
                                                value=ast.Name(id='child', ctx=ast.Load()),
                                                slice=ast.Index(value=ast.Constant(value='name')),
                                                ctx=ast.Load()
                                            ),
                                            ast.Subscript(
                                                value=ast.Name(id='child', ctx=ast.Load()),
                                                slice=ast.Index(value=ast.Constant(value='parent')),
                                                ctx=ast.Load()
                                            )
                                        ]
                                    )],
                                    keywords=[]
                                )
                            )
                        ],
                        orelse=[]
                    )
                ],
                orelse=[]
            ),
            # Loop through config['nodes']
            ast.For(
                target=ast.Name(id='node', ctx=ast.Store()),
                iter=ast.Subscript(
                    value=ast.Name(id='config', ctx=ast.Load()),
                    slice=ast.Index(value=ast.Constant(value='nodes')),
                    ctx=ast.Load()
                ),
                body=[
                    ast.If(
                        test=ast.UnaryOp(
                            op=ast.Not(),
                            operand=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(id='self', ctx=ast.Load()),
                                    attr='__addNode',
                                    ctx=ast.Load()
                                ),
                                args=[ast.Name(id='node', ctx=ast.Load())],
                                keywords=[]
                            )
                        ),
                        body=[ast.Return(value=None)],
                        orelse=[]
                    )
                ],
                orelse=[]
            ),
            # Logging and setting configuration validity
            astLogger('info', 'Done adding nodes ...', False),
            ast.Assign(
                targets=[ast.Attribute(
                    value=ast.Name(id='self', ctx=ast.Load()),
                    attr='valid_configuration',
                    ctx=ast.Store()
                )],
                value=ast.Constant(value=True)
            )
        ],
        decorator_list=[],
        returns=None
    )

    return function_def

def astAddNodeFunc():
    # Define the function
    function_def = ast.FunctionDef(
        name='__addNode',
        args=ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg='self'), ast.arg(arg='node_info')],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
            vararg=None,
            kwarg=None
        ),
        returns=ast.Name(id='bool', ctx=ast.Load()),
        body=[
            # If check for node_info being None
            ast.If(
                test=ast.Compare(
                    left=ast.Name(id='node_info', ctx=ast.Load()),
                    ops=[ast.Is()],
                    comparators=[ast.Constant(value=None)]
                ),
                body=[
                    ast.Expr(value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id='LOGGER', ctx=ast.Load()),
                            attr='error',
                            ctx=ast.Load()
                        ),
                        args=[ast.Constant(value="node cannot be null")],
                        keywords=[]
                    )),
                    ast.Return(value=ast.Constant(value=False))
                ],
                orelse=[]
            ),
            # Try block
            ast.Try(
                body=[
                    # Assign class from globals based on 'address'
                    ast.Assign(
                        targets=[ast.Name(id='cls', ctx=ast.Store())],
                        value=ast.Subscript(
                            value=ast.Call(
                                func=ast.Name(id='globals', ctx=ast.Load()),
                                args=[],
                                keywords=[]
                            ),
                            slice=ast.Index(value=ast.Subscript(
                                value=ast.Name(id='node_info', ctx=ast.Load()),
                                slice=ast.Index(value=ast.Constant(value='address')),
                                ctx=ast.Load()
                            )),
                            ctx=ast.Load()
                        )
                    ),
                    # Instantiate node object
                    ast.Assign(
                        targets=[ast.Name(id='node', ctx=ast.Store())],
                        value=ast.Call(
                            func=ast.Name(id='cls', ctx=ast.Load()),
                            args=[
                                ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='poly', ctx=ast.Load()),
                                ast.Subscript(
                                    value=ast.Name(id='node_info', ctx=ast.Load()),
                                    slice=ast.Index(value=ast.Constant(value='primaryNode')),
                                    ctx=ast.Load()
                                ),
                                ast.Subscript(
                                    value=ast.Name(id='node_info', ctx=ast.Load()),
                                    slice=ast.Index(value=ast.Constant(value='nodeDefId')),
                                    ctx=ast.Load()
                                ),
                                ast.Subscript(
                                    value=ast.Name(id='node_info', ctx=ast.Load()),
                                    slice=ast.Index(value=ast.Constant(value='name')),
                                    ctx=ast.Load()
                                )
                            ],
                            keywords=[]
                        )
                    ),
                    # Check if node instantiation was successful
                    ast.If(
                        test=ast.Compare(
                            left=ast.Name(id='node', ctx=ast.Load()),
                            ops=[ast.Is()],
                            comparators=[ast.Constant(value=None)]
                        ),
                        body=[
                            ast.Expr(value=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(id='LOGGER', ctx=ast.Load()),
                                    attr='error',
                                    ctx=ast.Load()
                                ),
                                args=[ast.JoinedStr(values=[
                                    ast.Str(s="invalid noddef id ...")
                                ])],
                                keywords=[]
                            )),
                            ast.Return(value=ast.Constant(value=False))
                        ],
                        orelse=[
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
                                args=[ast.Name(id='node', ctx=ast.Load())],
                                keywords=[]
                            )),
                            ast.Expr(
                                value=ast.Call(
                                    func=ast.Attribute(
                                    value=ast.Name(id='node', ctx=ast.Load()),
                                    attr='setProtocolHandler',
                                    ctx=ast.Load()
                                ),
                                args=[
                                    ast.Attribute(
                                    value=ast.Name(id='self', ctx=ast.Load()),
                                    attr='protocolHandler',
                                    ctx=ast.Load()
                                    )
                                ],
                                keywords=[]
                                )
                            ),
                            ast.Return(value=ast.Constant(value=True))
                        ]
                    )
                ],
                handlers=[
                    ast.ExceptHandler(
                        type=ast.Name(id='Exception', ctx=ast.Load()),
                        name=ast.Name(id='ex', ctx=ast.Store()),
                        body=[
                            ast.Expr(value=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(id='LOGGER', ctx=ast.Load()),
                                    attr='error',
                                    ctx=ast.Load()
                                ),
                                args=[ast.Call(
                                    func=ast.Name(id='str', ctx=ast.Load()),
                                    args=[ast.Name(id='ex', ctx=ast.Load())],
                                    keywords=[]
                                )],
                                keywords=[]
                            )),
                            ast.Return(value=ast.Constant(value=False))
                        ]
                    )
                ],
                orelse=[],
                finalbody=[]
            )
        ],
        decorator_list=[]
    )

    return function_def

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


def astCreateMainFunc(controller, protocolHandler):
    try_body = [
        # plugin = Plugin(PLUGIN_FILE_NAME)
        ast.Assign(
            targets=[ast.Name(id='plugin', ctx=ast.Store())],
            value=ast.Call(
                func=ast.Name(id='Plugin', ctx=ast.Load()),
                args=[ast.Name(id='PLUGIN_FILE_NAME', ctx=ast.Load())],
                keywords=[]
            )
        ),
        # plugin.toIoX()
        ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='plugin', ctx=ast.Load()),
                    attr='toIoX',
                    ctx=ast.Load()
                ),
                args=[],
                keywords=[]
            )
        ),
        # plugin.generateCode(path='./')
        ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='plugin', ctx=ast.Load()),
                    attr='generateCode',
                    ctx=ast.Load()
                ),
                args=[],
                keywords=[ast.keyword(arg='path', value=ast.Constant(value='./'))]
            )
        ),
        # protocolHandler = ModbusProtocolHandler(plugin)
        ast.Assign(
            targets=[ast.Name(id='protocolHandler', ctx=ast.Store())],
            value=ast.Call(
                func=ast.Name(id=protocolHandler, ctx=ast.Load()),
                args=[ast.Name(id='plugin', ctx=ast.Load())],
                keywords=[]
            )
        ),
        ast.Assign(
            targets=[ast.Name(id='polyglot', ctx=ast.Store())],
            value=ast.Call(
                func=ast.Attribute(value=ast.Name(id='udi_interface', ctx=ast.Load()), attr='Interface', ctx=ast.Load()),
                args=[ast.List(elts=[], ctx=ast.Load())],
                keywords=[]
            )
        ),
        ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='start', ctx=ast.Load()),
            args=[ast.Attribute(value=ast.Name(id='version', ctx=ast.Load()), attr='ud_plugin_version', ctx=ast.Load())],
            keywords=[]
        )),
        ast.Assign(
            targets=[ast.Name(id='controller', ctx=ast.Store())],
            value=ast.Call(
                func=ast.Name(id=controller, ctx=ast.Load()),
                args=[ast.Name(id='polyglot', ctx=ast.Load()), ast.Name(id='protocolHandler', ctx=ast.Load())],
                keywords=[]
            )
        ),
        ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Name(id='controller', ctx=ast.Load()), attr='start', ctx=ast.Load()),
            args=[],
            keywords=[]
        )),
        ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Name(id='polyglot', ctx=ast.Load()), attr='runForever', ctx=ast.Load()),
            args=[],
            keywords=[]
        ))
    ]

    # The except block handling KeyboardInterrupt and SystemExit
    except_handlers = [
        ast.ExceptHandler(
            type=ast.Tuple(elts=[
                ast.Name(id='KeyboardInterrupt', ctx=ast.Load()),
                ast.Name(id='SystemExit', ctx=ast.Load())
            ], ctx=ast.Load()),
            name=None,
            body=[
                ast.Expr(value=ast.Call(
                    func=ast.Attribute(value=ast.Name(id='LOGGER', ctx=ast.Load()), attr='info', ctx=ast.Load()),
                    args=[ast.Constant(value="exiting ...")],
                    keywords=[]
                )),
                ast.Expr(value=ast.Call(
                    func=ast.Name(id='sys', ctx=ast.Load()),
                    attr='exit',
                    args=[ast.Constant(value=0)],
                    keywords=[]
                ))
            ]
        )
    ]

    # The main if block
    main_if = ast.If(
        test=ast.Compare(
            left=ast.Name(id='__name__', ctx=ast.Load()),
            ops=[ast.Eq()],
            comparators=[ast.Constant(value="__main__")]
        ),
        body=[
            ast.Try(
                body=try_body,
                handlers=except_handlers,
                orelse=[],
                finalbody=[]
            )
        ],
        orelse=[]
    )

    return main_if

def astSetPluginFunc():
    return ast.FunctionDef(
    name='setProtocolHandler',
    args=ast.arguments(
        posonlyargs=[],
        args=[
            ast.arg(arg='self', annotation=None),
            ast.arg(arg='protocolHandler', annotation=None)
        ],
        vararg=None,
        kwonlyargs=[],
        kw_defaults=[],
        kwarg=None,
        defaults=[]
    ),
    body=[
        ast.Assign(
            targets=[
                ast.Attribute(
                    value=ast.Name(id='self', ctx=ast.Load()),
                    attr='protocolHandler',
                    ctx=ast.Store()
                )
            ],
            value=ast.Name(id='protocolHandler', ctx=ast.Load())
        )
    ],
    decorator_list=[],
    returns=None
    )

#protocol handler
def astPHQueryPropertyFunc(update_method, property):
    
    body=[
    # Outer if statement
        ast.If(
              test=ast.Attribute(
                value=ast.Name(id='self', ctx=ast.Load()),
                attr='protocolHandler',
                ctx=ast.Load()
        ),
        body=[
            # Assignment statement
            ast.Assign(
                targets=[ast.Name(id='val', ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Attribute(
                            value=ast.Name(id='self', ctx=ast.Load()),
                            attr='protocolHandler',
                            ctx=ast.Load()
                        ),
                        attr='queryProperty',
                        ctx=ast.Load()
                    ),
                    args=[
                        ast.Name(id='self', ctx=ast.Load()),
                        ast.Constant(value=property)
                    ],
                    keywords=[]
                )
            ),
            # Inner if statement
            ast.If(
                test=ast.Compare(
                left=ast.Name(id='val', ctx=ast.Load()),
                ops=[ast.NotEq()],
                comparators=[ast.Constant(value=None)]),
                body=[
                    # Method call within the inner if statement
                    ast.Expr(
                        value=ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id='self', ctx=ast.Load()),
                                attr=update_method,
                                ctx=ast.Load()
                            ),
                            args=[
                                ast.Name(id='val', ctx=ast.Load()),
                                ast.Constant(value=True)
                            ],
                            keywords=[]
                        )
                    ),
                    # Return statement within the inner if statement
                    ast.Return(value=ast.Constant(value=True))
                ],
                orelse=[]
            )
        ],
        orelse=[],
    ),
    ast.Return(value=ast.Constant(value=False))
    ]
    return body

#protocol handler
def astPHSetPropertyFunc(update_method, property):
    
    body=[
    # Outer if statement
        ast.If(
              test=ast.Attribute(
                value=ast.Name(id='self', ctx=ast.Load()),
                attr='protocolHandler',
                ctx=ast.Load()
        ),
        body=[
            # Inner if statement
            ast.If(
                test=ast.Call(
                    func=ast.Attribute(
                            value=ast.Attribute(
                                value=ast.Name(id='self', ctx=ast.Load()),
                                attr='protocolHandler',
                                ctx=ast.Load()
                            ),
                            attr='setProperty',
                            ctx=ast.Load()
                    ),
                    args=[
                        ast.Name(id='self', ctx=ast.Load()),
                        ast.Constant(value=property),
                        ast.Name(id=property, ctx=ast.Load())
                    ],
                    keywords=[]
                ),
                body=[
                    # Method call within the inner if statement
                    ast.Expr(
                        value=ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id='self', ctx=ast.Load()),
                                attr=update_method,
                                ctx=ast.Load()
                            ),
                            args=[
                                ast.Name(id=property, ctx=ast.Load()),
                                ast.Constant(value=True)
                            ],
                            keywords=[]
                        )
                    ),
                    # Return statement within the inner if statement
                    ast.Return(value=ast.Constant(value=True))
                ],
                orelse=[]
            )
        ],
        orelse=[],
    ),
    ast.Return(value=ast.Constant(value=False))
    ]
    return body

def astPHProcessCommandFunc(command_name, args):

    arg_nodes = [ast.Name(id='self', ctx=ast.Load()),ast.Constant(value=command_name) ] 
    #for arg in args_array:
    #    arg_nodes.append(ast.Name(id=arg, ctx=ast.Load))
    # Create AST node for function call
    return_statement = ast.Return(
            value=ast.Call(
            func=ast.Name(id='self.protocolHandler.processCommand', ctx=ast.Load()),
            args= arg_nodes,
            keywords=[
                ast.keyword(
                    arg=key,
                    value=ast.Name(id=val, ctx=ast.Load())
                ) for key, val in args.items()
            ]
        )
    )

    body=[
    # Outer if statement
        ast.If(
              test=ast.Attribute(
              value=ast.Name(id='self', ctx=ast.Load()),
              attr='protocolHandler',
              ctx=ast.Load()
        ),
        body=[
            return_statement
        ],
        orelse=[],
    ),
    ast.Return(value=ast.Constant(value=False))
    ]
    return body
