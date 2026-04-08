from graph.graph import app


result = app.invoke({
    "messages": [],
    "directory": "/Users/Dylan/Documents/desordenados",
    "file_list": "",
    "metadata": [],
    "errors": []
})


for file in result['metadata']:
    print(file)

print(result['file_list'])
print(f"archivos procesados {len(result['metadata'])}")
print(f"errores: {result['errors']}")


