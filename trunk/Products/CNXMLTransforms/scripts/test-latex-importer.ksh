#! /usr/bin/ksh -vx

# usage: /test-latex-importer.ksh tests-file test-dir results-base-dir

tests=${1}
testdir=${2}
resultsbasedir=${3}

# ${tests} file contains a list of tests of the form: <test-name>/<zip-name>
# ${testdir} is the directory where each of the tests in ${tests} can be found
# => ${testdir}/<test-name>/<zip-name> is the full path to the test.

workdir=/tmp/dirname.$$

timestamp=$(date +%F-%T)
resultsdir=$(echo ${resultsbasedir}'/'${timestamp})

cxnmltransforms=/opt/instances/cnx/Products/Rhaptos/CNXMLTransforms-latex
xsldir=${cxnmltransforms}/www
LatexImport=${cxnmltransforms}/LatexImport.ksh

# open input file ${tests} and assign to the '3' file descriptor
exec 3< ${tests}
while read -u3 test; do
    zipfile=${test##*/}
    basename=${zipfile%.zip}
    testname=${test%/*.zip}

    zippath=${testdir}/${test}

    thisworkdir=${workdir}/${testname}
    mkdir -p ${thisworkdir}

    thisresultdir=${resultsdir}/${testname}
    mkdir -p ${thisresultdir}

    cnxmlfile=${thisworkdir}/index.cnxml
    ${LatexImport} "${basename}" "${zippath}" "${thisworkdir}" "${xsldir}"
    if [[ -s ${cnxmlfile} ]]; then
        cp ${cnxmlfile} ${thisresultdir}/
    fi
done

# diff -r ${resultsdir} ${old-resultsdir} - can be used to compared this run against prior runs
