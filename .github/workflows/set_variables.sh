#!/bin/bash

#set -eu
set -x

if test "${OS_VERSION:-}" = ""; then
    echo "ERROR: OS_VERSION env is empty"
    exit 1
fi

TAG=
DEP_BRANCH=
TARGET_DIR=
DEP_DIR=

case "${GITHUB_EVENT_NAME}" in
    repository_dispatch)
        B=${PAYLOAD_BRANCH};;
    pull_request)
        case "${GITHUB_BASE_REF}" in
            master | integration | experimental* | release_* | ci* | pci*)
                B=${GITHUB_BASE_REF};;
            *)
                B=null;
        esac;;
    push)
        case "${GITHUB_REF}" in
            refs/tags/v*)
                B=`git branch -a --contains "${GITHUB_REF}" | grep remotes | grep release_ | cut -d"/" -f3`;;
            refs/heads/*)
                B=${GITHUB_REF#refs/heads/};;
            *)
                B=null;
        esac;;
esac
if [ -z ${B} ]; then
  B=null
fi
if [ "${GITHUB_EVENT_NAME}" != "repository_dispatch" ]; then
    case "${GITHUB_REF}" in
        refs/heads/experimental* | refs/heads/master | refs/heads/release_*)
            DEP_BRANCH=${B}
            DEP_DIR=${B##release_}
            TARGET_DIR=${B##release_};;
        refs/heads/integration | refs/heads/ci* | refs/heads/pci*)
            DEP_BRANCH=integration
            DEP_DIR=master
            TARGET_DIR=master;;
        refs/tags/v*)
            TAG=${GITHUB_REF#refs/tags/}
            DEP_BRANCH=${B}
            DEP_DIR=${B##release_}
            TARGET_DIR=${B##release_};;
        refs/pull/*)
case "${B}" in
                integration | ci* | pci*)
                    DEP_BRANCH=integration
                    DEP_DIR=master
                    TARGET_DIR=master;;
                *)
                    DEP_BRANCH=${B}
                    DEP_DIR=${B##release_}
                    TARGET_DIR=${B##release_};;
            esac;;
    esac
else
    # GITHUB_REF is always "refs/heads/master" in this case (repository_dispatch)
    case "${B}" in
        master | experimental* | release_*)
            DEP_BRANCH=${B}
            DEP_DIR=${B##release_}
            TARGET_DIR=${B##release_};;
        integration | ci* | pci*)
            DEP_BRANCH=integration
            DEP_DIR=master
            TARGET_DIR=master;;
    esac
fi

if [ -z ${TAG} ]; then
  CI=continuous_integration
else
  CI=releases
fi


    
        
    
    


echo "::set-output name=branch::${B}"
echo "::set-output name=tag::${TAG}"
echo "::set-output name=dep_branch::${DEP_BRANCH}"
echo "::set-output name=target_dir::${TARGET_DIR}"
echo "::set-output name=dep_dir::${DEP_DIR}"
echo "::set-output name=buildimage::metwork/mfxxx-${OS_VERSION}-buildimage:${DEP_BRANCH}"
echo "::set-output name=testimage::metwork/mfxxx-${OS_VERSION}-testimage:${DEP_BRANCH}"
echo "::set-output name=buildlog_dir::/pub/metwork/${CI}/buildlogs/${B}/mfdata/${OS_VERSION}/${GITHUB_RUN_NUMBER}"
echo "::set-output name=rpm_dir::/pub/metwork/${CI}/rpms/${B}/${OS_VERSION}"
echo "::set-output name=doc_dir::/pub/metwork/${CI}/docs/${B}/mfdata"
