if ! [ -z "$1" ]
then
    DOCS_DIR=$1
else
    DOCS_DIR=$RAFIKI_VERSION
fi 

pip install sphinx sphinx_rtd_theme
sphinx-build -b html docs/ docs/$DOCS_DIR/

echo "Generated documentation site at ./docs/$DOCS_DIR/index.html"