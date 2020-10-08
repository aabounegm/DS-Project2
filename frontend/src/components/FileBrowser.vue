<template>
  <v-card class="mx-auto" :loading="loading">
    <Toolbar
      :path="path"
      :storages="storages"
      :baseUrl="activeStorage.url"
      :remaining-storage="remainingStorage"
      @storage-changed="activeStorage = $event"
      @path-changed="pathChanged"
      @add-files="addUploadingFiles"
      @folder-created="refreshPending = true"
    />
    <v-row no-gutters>
      <v-col sm="auto">
        <Tree
          :path="path"
          :icons="icons"
          :refreshPending="refreshPending"
          :base-url="activeStorage.url"
          @path-changed="pathChanged"
          @loading="loading = $event"
          @refreshed="refreshPending = false"
          @init="remainingStorage = $event"
        />
      </v-col>
      <v-divider vertical />
      <v-col>
        <List
          :path="path"
          :base-url="activeStorage.url"
          :icons="icons"
          :refreshPending="refreshPending"
          @path-changed="pathChanged"
          @loading="loading = $event"
          @refreshed="refreshPending = false"
          @file-deleted="refreshPending = true"
        />
      </v-col>
    </v-row>
    <Upload
      v-if="uploadingFiles.length !== 0"
      :path="path"
      :storage="activeStorage"
      :files="uploadingFiles"
      :icons="icons"
      :base-url="activeStorage.url"
      :maxUploadFilesCount="maxUploadFilesCount"
      :maxUploadFileSize="maxUploadFileSize"
      @add-files="addUploadingFiles"
      @remove-file="removeUploadingFile"
      @cancel="uploadingFiles = []"
      @uploaded="uploaded"
    />
  </v-card>
</template>

<script lang="ts">
import Vue, { PropType } from 'vue';
import Toolbar from '@/components/Toolbar.vue';
import Tree from '@/components/Tree.vue';
import List from '@/components/List.vue';
import Upload from '@/components/Upload.vue';
import { Remote } from '@/types';

const fileIcons = {
  zip: 'mdi-folder-zip-outline',
  rar: 'mdi-folder-zip-outline',
  htm: 'mdi-language-html5',
  html: 'mdi-language-html5',
  js: 'mdi-nodejs',
  json: 'mdi-json',
  md: 'mdi-markdown',
  pdf: 'mdi-file-pdf',
  png: 'mdi-file-image',
  jpg: 'mdi-file-image',
  jpeg: 'mdi-file-image',
  mp4: 'mdi-filmstrip',
  mkv: 'mdi-filmstrip',
  avi: 'mdi-filmstrip',
  wmv: 'mdi-filmstrip',
  mov: 'mdi-filmstrip',
  txt: 'mdi-file-document-outline',
  xls: 'mdi-file-excel',
  other: 'mdi-file-outline',
};

export default Vue.extend({
  components: {
    Toolbar,
    Tree,
    List,
    Upload,
  },
  model: {
    prop: 'path',
    event: 'change',
  },
  props: {
    storages: {
      type: Array as PropType<Remote[]>,
    },
    // max files count to upload at once. Unlimited by default
    maxUploadFilesCount: { type: Number, default: Infinity },
    // max file size to upload. Unlimited by default
    maxUploadFileSize: { type: Number, default: Infinity },
  },
  data () {
    return {
      loading: false,
      remainingStorage: 0,
      path: '',
      activeStorage: this.storages[0],
      uploadingFiles: [] as File[], // or an Array of files
      refreshPending: false,
      icons: fileIcons,
    };
  },
  methods: {
    addUploadingFiles (filelist: FileList) {
      let files = Array.from(filelist);

      if (this.maxUploadFileSize) {
        files = files.filter(
          file => file.size <= this.maxUploadFileSize,
        );
      }

      if (this.uploadingFiles.length === 0) {
        this.uploadingFiles = [];
      }

      if (this.maxUploadFilesCount && this.uploadingFiles.length + files.length > this.maxUploadFilesCount) {
        files = files.slice(0, this.maxUploadFilesCount - this.uploadingFiles.length);
      }

      this.uploadingFiles.push(...files);
    },
    removeUploadingFile (index: number) {
      this.uploadingFiles.splice(index, 1);
    },
    uploaded (remaining: number) {
      this.remainingStorage = remaining;
      this.uploadingFiles = [];
      this.refreshPending = true;
    },
    pathChanged (path: string) {
      this.path = path;
      this.$emit('change', path);
    },
  },
  created () {
    this.activeStorage = this.storages[0];
  },
  mounted () {
    if (!this.path && this.$vuetify.breakpoint.xsOnly) {
      this.pathChanged('/');
    }
  },
  watch: {
    activeStorage: {
      immediate: true,
      async handler (value: Remote) {
        const res = await fetch(`${value.url}/free_space`);
        this.remainingStorage = await res.json();
      },
    },
  },
});
</script>
