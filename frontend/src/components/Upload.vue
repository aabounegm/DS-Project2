<template>
  <v-overlay :absolute="true">
    <v-card flat light class="mx-auto" :loading="loading">
      <v-card-text class="py-3 text-center">
        <div>
          <span class="grey--text">Upload to:</span>
          <v-chip color="info" class="mx-1">{{ storage.name }}</v-chip>
          <v-chip>{{ path }}</v-chip>
        </div>
        <div v-if="maxUploadFilesCount">
          <span class="grey--text">Max files count:
            <v-icon small v-if="maxUploadFilesCount === Infinity">mdi-infinity</v-icon>
            <span v-else>maxUploadFilesCount</span>
          </span>
        </div>
        <div v-if="maxUploadFileSize">
          <span class="grey--text">Max file size:
            <v-icon small v-if="maxUploadFileSize === Infinity">mdi-infinity</v-icon>
            <span v-else>{{ formatBytes(maxUploadFileSize) }}</span>
          </span>
        </div>
      </v-card-text>
      <v-divider />
      <v-card-text v-if="listItems.length" class="pa-0 files-list-wrapper">
        <v-list two-line v-if="listItems.length">
          <v-list-item v-for="(file, index) in listItems" :key="index">
            <v-list-item-avatar>
              <v-img v-if="file.preview" :src="file.preview" />
              <v-icon
                v-else
                v-text="icons[file.extension] || 'mdi-file'"
                class="mdi-36px"
              />
            </v-list-item-avatar>
            <v-list-item-content>
              <v-list-item-title v-text="file.name" />
              <v-list-item-subtitle>{{ formatBytes(file.size) }} &mdash; {{ file.type }}</v-list-item-subtitle>
            </v-list-item-content>
            <v-list-item-action>
              <v-btn icon @click="remove(index)">
                <v-icon>mdi-close</v-icon>
              </v-btn>
            </v-list-item-action>
          </v-list-item>
        </v-list>
      </v-card-text>
      <v-card-text v-else class="py-6 text-center">
        <v-btn @click="$refs.inputUpload.click()">
          <v-icon left>mdi-plus-circle</v-icon>
          Add files
        </v-btn>
      </v-card-text>
      <v-divider />
      <v-toolbar dense flat>
        <div class="grow"></div>
        <v-btn text @click="cancel" class="mx-1">Cancel</v-btn>
        <v-btn
          :disabled="listItems.length >= maxUploadFilesCount"
          depressed
          color="info"
          @click="$refs.inputUpload.click()"
          class="mx-1"
        >
          <v-icon left>mdi-plus-circle</v-icon>
          Add Files
          <input
            v-show="false"
            ref="inputUpload"
            type="file"
            multiple
            @change="add"
          />
        </v-btn>
        <v-btn depressed color="success" @click="upload" class="ml-1" :disabled="!files || loading">
          Upload
          <v-icon right>mdi-upload-outline</v-icon>
        </v-btn>
      </v-toolbar>
      <v-overlay :value="uploading" :absolute="true" color="white" opacity="0.9">
        <v-progress-linear :active="loading" indeterminate height="25" striped rounded reactive />
      </v-overlay>
    </v-card>
  </v-overlay>
</template>

<script lang="ts">
import formatBytes from '@/utils/formatBytes';
import { Icons, MyFile, Remote } from '@/types';
import Vue, { PropType } from 'vue';

const imageMimeTypes = ['image/png', 'image/jpeg'];

export default Vue.extend({
  props: {
    path: {
      type: String,
    },
    storage: {
      type: Object as PropType<Remote>,
    },
    baseUrl: {
      type: String,
    },
    files: {
      type: Array as PropType<File[]>,
      default: () => [],
    },
    icons: {
      type: Object as PropType<Icons>,
    },
    maxUploadFilesCount: {
      type: Number,
      default: Infinity,
    },
    maxUploadFileSize: {
      type: Number,
      default: Infinity,
    },
  },
  data () {
    return {
      loading: false,
      uploading: false,
      progress: 0,
      listItems: [] as MyFile[],
    };
  },
  methods: {
    formatBytes,
    async filesMap (files: File[]) {
      const promises: Promise<MyFile>[] = Array.from(files).map(file => {
        const result: MyFile = {
          name: file.name,
          type: file.type,
          size: file.size,
          extension: file.name.split('.').pop(),
          preview: '',
        };
        return new Promise(resolve => {
          if (!imageMimeTypes.includes(result.type)) {
            return resolve(result);
          }
          const reader = new FileReader();
          reader.onload = function (e) {
            if (e.target == null) {
              return;
            }
            result.preview = e.target.result as string;
            resolve(result);
          };
          reader.readAsDataURL(file);
        });
      });

      return await Promise.all(promises);
    },
    async add (event: InputEvent) {
      if (event.target == null) {
        return;
      }
      const input = event.target as HTMLInputElement;
      if (input.files == null) {
        return;
      }
      const files = Array.from(input.files);
      this.$emit('add-files', files);
      (this.$refs.inputUpload as HTMLInputElement).value = '';
    },
    remove (index: number) {
      this.$emit('remove-file', index);
      this.listItems.splice(index, 1);
    },
    cancel () {
      this.$emit('cancel');
      this.listItems = [];
    },
    async upload () {
      let remainingStorageSize;
      for (const file of this.files) {
        const formData = new FormData();
        formData.append('file', file, file.name);
        const url = `${this.baseUrl}/file${this.path}${file.name}`;

        this.uploading = true;

        try {
          const response = await fetch(url, {
            method: 'post',
            body: formData,
          });
          if (!response.ok) {
            throw await response.text();
          }
          remainingStorageSize = await response.json();
        } catch (error) {
          console.error(error);
          alert('An error occured. Check the console');
        }
      }
      this.uploading = false;
      this.$emit('uploaded', remainingStorageSize);
    },
  },
  watch: {
    files: {
      deep: true,
      immediate: true,
      async handler () {
        this.loading = true;
        this.listItems = await this.filesMap(this.files);
        this.loading = false;
      },
    },
  },
});
</script>

<style lang="scss" scoped>
::v-deep .v-overlay__content {
  width: 90%;
  max-width: 500px;

  .files-list-wrapper {
    max-height: 250px;
    overflow-y: auto;
  }
}
</style>
