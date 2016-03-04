#!/bin/sh

rm -rf resources
mkdir resources

function package() {
    local file="$1"
    ln -s "../$file" "resources/$file"
}

package tbontb
package tbontb.json
package tbontb.svg

tar -czh -f resources.tar.gz resources
rm -r resources
