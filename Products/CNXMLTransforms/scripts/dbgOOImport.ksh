#! /usr/bin/ksh -vx

# print PDW is ${DOCDIR}

INSTALLDIR=/opt/instances/cnx

DOCDIR=/home/bnwest/CODE/OOImportDocs

cd ${DOCDIR}
#for file in *.doc
#do
#file='NASA__foodandwater.dot'
file=$1
    # if the file has no expected extension, add one and try script
    print $file

    # sed is our friend
    # better_filebase=$(print $filebase | sed 's/ /_/g' | sed 's/,/_/g' )
    better_wordfile=$(print ${file} | sed 's/ /_/g' | sed 's/,/_/g' | sed 's/\[/_/g' | sed 's/\]/_/g' | sed 's/%20/_/g' | sed "s/'/_/g" | sed "s/’/_/g" | sed 's/"/_/g' | sed "s/”/_/g" | sed 's/“/_/g')
    wordfilebase=${better_wordfile%.*}
    extension=${better_wordfile##*.}
    better_filebase=$(print ${wordfilebase} | sed 's/\./_/g' )

    if [[ ! -d "${DOCDIR}/${better_filebase}" ]]; then
        mkdir "${DOCDIR}/${better_filebase}"
        chmod 777 "${DOCDIR}/${better_filebase}"
    fi

    # created macro by hand: Standard.Module1.SaveAsOOO()
    #    based on code from http://www.oooforum.org/forum/viewtopic.phtml?t=3772
    # prefer to have macro in a standalone file and access via command line.
    # macro forces the .doc file to be saved as a .sxw file
    if [[ ${extension} != "sxw" ]]; then
        /usr/bin/soffice -invisible "macro:///Standard.Module1.SaveAsOOO(${DOCDIR}/$file)"
    fi

    if [[ -a ${DOCDIR}/${wordfilebase}.sxw ]]; then
        sxwfile=${DOCDIR}/${wordfilebase}.sxw
        sxwfile_ext='sxw'
    elif [[ -a ${DOCDIR}/${wordfilebase}.xxx ]]; then
        sxwfile=${DOCDIR}/${wordfilebase}.xxx
        sxwfile_ext='xxx'
    elif [[ -a ${DOCDIR}/${wordfilebase}.dxxx ]]; then
        sxwfile=${DOCDIR}/${wordfilebase}.dxxx
        sxwfile_ext='dxxx'
    else
        sh -c 'sleep 10'
        if [[ -a ${DOCDIR}/${wordfilebase}.sxw ]]; then
            sxwfile=${DOCDIR}/${wordfilebase}.sxw
            sxwfile_ext='sxw'
        elif [[ -a ${DOCDIR}/${wordfilebase}.xxx ]]; then
            sxwfile=${DOCDIR}/${wordfilebase}.xxx
            sxwfile_ext='xxx'
        elif [[ -a ${DOCDIR}/${wordfilebase}.dxxx ]]; then
            sxwfile=${DOCDIR}/${wordfilebase}.dxxx
            sxwfile_ext='dxxx'
        else
            sh -c 'sleep 20'
            if [[ -a ${DOCDIR}/${wordfilebase}.sxw ]]; then
                sxwfile=${DOCDIR}/${wordfilebase}.sxw
                sxwfile_ext='sxw'
            elif [[ -a ${DOCDIR}/${wordfilebase}.xxx ]]; then
                sxwfile=${DOCDIR}/${wordfilebase}.xxx
                sxwfile_ext='xxx'
            elif [[ -a ${DOCDIR}/${wordfilebase}.dxxx ]]; then
                sxwfile=${DOCDIR}/${wordfilebase}.dxxx
                sxwfile_ext='dxxx'
            else
                sh -c 'sleep 30'
                if [[ -a ${DOCDIR}/${wordfilebase}.sxw ]]; then
                    sxwfile=${DOCDIR}/${wordfilebase}.sxw
                    sxwfile_ext='sxw'
                elif [[ -a ${DOCDIR}/${wordfilebase}.xxx ]]; then
                    sxwfile=${DOCDIR}/${wordfilebase}.xxx
                    sxwfile_ext='xxx'
                elif [[ -a ${DOCDIR}/${wordfilebase}.dxxx ]]; then
                    sxwfile=${DOCDIR}/${wordfilebase}.dxxx
                    sxwfile_ext='dxxx'
                else
                    sxwfile=""
                    exit
                fi
            fi
        fi
    fi

    if [[ sxwfile != "" ]]; then
        file "${sxwfile}"

        unzip -l "${sxwfile}"
        rc=$?
        if (( rc != 0 )); then
            sh -c 'sleep 10'
            unzip -l "${sxwfile}"
            rc=$?
            if (( rc != 0 )); then
                sh -c 'sleep 20'
                unzip -l "${sxwfile}"
                rc=$?
                if (( rc != 0 )); then
                    sh -c 'sleep 30'
                fi
            fi
        fi

        # move created ODT/SWX file
        mv "${sxwfile}" "${DOCDIR}/${better_filebase}/${better_filebase}.${sxwfile_ext}"
        sxwfile=${DOCDIR}/${better_filebase}/${better_filebase}.${sxwfile_ext}

        # fetch the OO xml file
        xmlfile=content.xml
        unzip -o "${sxwfile}" ${xmlfile} -d "${DOCDIR}/${better_filebase}"
        unzip -o "${sxwfile}" styles.xml -d "${DOCDIR}/${better_filebase}"
        if [[ -a "${DOCDIR}/${better_filebase}/${xmlfile}" ]]; then
            # rename the xml file
            mv "${DOCDIR}/${better_filebase}/${xmlfile}" "${DOCDIR}/${better_filebase}/${better_filebase}.xml"
            xmlfile=${DOCDIR}/${better_filebase}/${better_filebase}.xml
            touch ${xmlfile} # unzip gives the wrong timestamp
            tidyxmlfile=${DOCDIR}/${better_filebase}/${better_filebase}.tidy.xml
            tidy -quiet -xml -indent -output "${tidyxmlfile}" "${xmlfile}"

            # fetch images files from zipped sxw file

            # xform
            xmlfilebase=${DOCDIR}/${better_filebase}/${better_filebase}
            cnxmlfile=${DOCDIR}/${better_filebase}/${better_filebase}.cnxml
            xslfile=${INSTALLDIR}/Products/Rhaptos/CNXMLTransforms/www/oo2cnxml.xsl

            # front door - use our CNX logic which includes adding sections to OOo XML & post xform validation
            # try:
                # front door - use our CNX logic which includes adding sections to OOo XML & post xform validation
                print sudo ${INSTALLDIR}/bin/zopectl run ${INSTALLDIR}/Products/Rhaptos/CNXMLTransforms/scripts/dbgOOoImport.py "${sxwfile}" "${xmlfile}" "${xmlfilebase}" "${cnxmlfile}"
                cd ${INSTALLDIR}/Products/Rhaptos/CNXMLTransforms/
                sudo ${INSTALLDIR}/bin/zopectl run ./scripts/dbgOOoImport.py "${sxwfile}" "${xmlfile}" "${xmlfilebase}" "${cnxmlfile}"
            # except:
            #     print "dbgOOoImport.py raised an excpetion"
            #     # or back door - simple xform
            #     print xsltproc -o "${cnxmlfile}" "${xslfile}" "${tidyxmlfile}"
            #     xsltproc -o "${cnxmlfile}" "${xslfile}" "${tidyxmlfile}"
        fi
    fi
    exit
#done


