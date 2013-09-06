#!/bin/bash
# copy FACP XSLT transform files to their production locations

SRC="../Indexer/transform"
DEST="/srv/ha/web"

cp $SRC/fcac-eaccpf-to-solr.xsl $DEST/FCAC/etc/
cp $SRC/fcna-eaccpf-to-solr.xsl $DEST/FCNA/etc/
cp $SRC/fcns-eaccpf-to-solr.xsl $DEST/FCNS/etc/
cp $SRC/fcnt-eaccpf-to-solr.xsl $DEST/FCNT/etc/
cp $SRC/fcqd-eaccpf-to-solr.xsl $DEST/FCQD/etc/
cp $SRC/fcsa-eaccpf-to-solr.xsl $DEST/FCSA/etc/
cp $SRC/fcts-eaccpf-to-solr.xsl $DEST/FCTS/etc/
cp $SRC/fcvc-eaccpf-to-solr.xsl $DEST/FCVC/etc/
cp $SRC/fcwa-eaccpf-to-solr.xsl $DEST/FCWA/etc/
