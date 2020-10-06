<template>
  <v-toolbar flat dense color="blue-grey lighten-5">
    <v-toolbar-items>
      <v-menu offset-y v-if="storages.length > 1">
        <template #activator="{ on }">
          <v-btn icon class="storage-select-button mr-3" v-on="on">
            <v-icon>mdi-arrow-down-drop-circle-outline</v-icon>
          </v-btn>
        </template>
        <v-list class="storage-select-list">
          <v-list-item
            v-for="(item, index) in storages"
            :key="index"
            :disabled="item.url === currentStorage.url"
            @click="changeStorage(item.url)"
          >
            <v-list-item-icon>
              <v-icon v-text="item.icon" />
            </v-list-item-icon>
            <v-list-item-title v-text="item.name" />
          </v-list-item>
        </v-list>
      </v-menu>
      <v-btn text :input-value="path === '/'" @click="changePath('/')">
        <v-icon class="mr-2">{{currentStorage.icon}}</v-icon>
        {{currentStorage.name}}
      </v-btn>
      <template v-for="(segment, index) in pathSegments">
        <v-icon :key="index + '-icon'">mdi-chevron-right</v-icon>
        <v-btn
          text
          :input-value="index === pathSegments.length - 1"
          :key="index + '-btn'"
          @click="changePath(segment.path)"
        >{{ segment.name }}</v-btn>
      </template>
    </v-toolbar-items>
    <div class="flex-grow-1"></div>

    <template v-if="$vuetify.breakpoint.smAndUp">
      <v-tooltip bottom v-if="pathSegments.length > 0">
        <template #activator="{ on }">
          <v-btn icon @click="goUp" v-on="on">
            <v-icon>mdi-arrow-up-bold-outline</v-icon>
          </v-btn>
        </template>
        <span v-if="pathSegments.length === 1">Up to "root"</span>
        <span v-else>Up to "{{pathSegments[pathSegments.length - 2].name}}"</span>
      </v-tooltip>
      <v-menu
        v-model="newFolderPopper"
        :close-on-content-click="false"
        :nudge-width="200"
        offset-y
      >
        <template #activator="{ on }">
          <v-btn v-if="path" icon v-on="on" title="Create Folder">
            <v-icon>mdi-folder-plus-outline</v-icon>
          </v-btn>
        </template>
        <v-card>
          <v-card-text>
            <v-text-field label="Name" v-model="newFolderName" hide-details />
          </v-card-text>
          <v-card-actions>
            <div class="flex-grow-1"></div>
            <v-btn @click="newFolderPopper = false" depressed>Cancel</v-btn>
            <v-btn
              color="success"
              :disabled="!newFolderName"
              depressed
              @click="mkdir"
            >Create Folder</v-btn>
          </v-card-actions>
        </v-card>
      </v-menu>
      <v-tooltip bottom v-if="path">
        <template #activator="{ on }">
          <v-btn v-on="on" icon @click="$refs.inputUpload.click()">
            <v-icon>mdi-plus-circle</v-icon>
            <input v-show="false" ref="inputUpload" type="file" multiple @change="addFiles" />
          </v-btn>
        </template>
        <span>Upload files</span>
      </v-tooltip>
    </template>
  </v-toolbar>
</template>

<script lang="ts">
import Vue, { PropType } from 'vue';
import { Remote } from '@/types';

export default Vue.extend({
  props: {
    storages: {
      type: Array as PropType<Remote[]>,
    },
    baseUrl: {
      type: String,
    },
    path: {
      type: String,
    },
  },
  data () {
    return {
      newFolderPopper: false,
      newFolderName: '',
    };
  },
  computed: {
    pathSegments (): {name: string; path: string}[] {
      let path = '/';
      const thisPath = this.path as string;
      const isFolder = thisPath[thisPath.length - 1] === '/';
      const segments = thisPath.split('/').filter(item => item);

      const segmentsDetailed = segments.map((item, index) => {
        path += item + (index < segments.length - 1 || isFolder ? '/' : '');
        return {
          name: item,
          path,
        };
      });

      return segmentsDetailed;
    },
    currentStorage () {
      return this.storages.find(item => item.url === this.baseUrl);
    },
  },
  methods: {
    changeStorage (url: string) {
      if (this.baseUrl === url) { return; }

      const storage = this.storages.find(s => s.url === url);
      if (storage == null) { return; }

      this.$emit('storage-changed', storage);
      this.$emit('path-changed', '');
    },
    changePath (path: string) {
      this.$emit('path-changed', path);
    },
    goUp () {
      const segments = this.pathSegments;
      const path =
          segments.length === 1
            ? '/'
            : segments[segments.length - 2].path;
      this.changePath(path);
    },
    async addFiles (event: InputEvent) {
      if (event.target == null) {
        return;
      }
      const input = event.target as HTMLInputElement;
      this.$emit('add-files', input.files);
      (this.$refs.inputUpload as HTMLInputElement).value = '';
    },
    async mkdir () {
      this.$emit('loading', true);

      const url = `${this.baseUrl}/dir/${this.path}/${this.newFolderName}`;

      try {
        const res = await fetch(url, {
          method: 'post',
        });
        if (!res.ok) {
          throw await res.text();
        }
        this.$emit('folder-created', this.newFolderName);

        this.newFolderPopper = false;
        this.newFolderName = '';
      } catch (error) {
        console.error(error);
        alert('An error occured. Check the console');
      }

      this.$emit('loading', false);
    },
  },
});
</script>

<style lang="scss" scoped>
/* Storage Menu - alternate appearance
.storage-select-button ::v-deep .v-btn__content {
  flex-wrap: wrap;
  font-size: 11px;

  .v-icon {
    width: 100%;
    font-size: 22px;
  }
}
*/

.storage-select-list .v-list-item--disabled {
  background-color: rgba(0, 0, 0, 0.25);
  color: #fff;

  .v-icon {
    color: #fff;
  }
}
</style>
