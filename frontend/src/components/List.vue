<template>
  <v-card flat tile min-height="380" class="d-flex flex-column">
    <confirm ref="confirm"></confirm>
    <v-card-text
      v-if="!path"
      class="grow d-flex justify-center align-center grey--text"
    >Select a folder or a file</v-card-text>
    <v-card-text
      v-else-if="isFile"
      class="grow d-flex justify-center align-center"
    >File: {{ path }}</v-card-text>
    <v-card-text v-else-if="dirs.length || files.length" class="grow">
      <v-list subheader v-if="dirs.length">
        <v-subheader>Folders</v-subheader>
        <v-list-item
          v-for="item in dirs"
          :key="item.name"
          @click="changePath(item.path)"
          class="pl-0"
        >
          <v-list-item-avatar class="ma-0">
            <v-icon>mdi-folder-outline</v-icon>
          </v-list-item-avatar>
          <v-list-item-content class="py-2">
            <v-list-item-title v-text="item.name"></v-list-item-title>
          </v-list-item-content>
          <v-list-item-action>
            <v-btn icon @click.stop="deleteItem(item)">
              <v-icon color="grey lighten-1">mdi-delete-outline</v-icon>
            </v-btn>
            <v-btn icon v-if="false">
              <v-icon color="grey lighten-1">mdi-information</v-icon>
            </v-btn>
          </v-list-item-action>
        </v-list-item>
      </v-list>
      <v-divider v-if="dirs.length && files.length"></v-divider>
      <v-list subheader v-if="files.length">
        <v-subheader>Files</v-subheader>
        <v-list-item
          v-for="item in files"
          :key="item.name"
          @click="changePath(item.path)"
          class="pl-0"
        >
          <v-list-item-avatar class="ma-0">
            <v-icon>{{ icons[item.extension] || icons['other'] }}</v-icon>
          </v-list-item-avatar>

          <v-list-item-content class="py-2">
            <v-list-item-title v-text="item.basename"></v-list-item-title>
            <v-list-item-subtitle>{{ formatBytes(item.size) }}</v-list-item-subtitle>
          </v-list-item-content>

          <v-list-item-action>
            <v-btn icon @click.stop="deleteItem(item)">
              <v-icon color="grey lighten-1">mdi-delete-outline</v-icon>
            </v-btn>
            <v-btn icon v-if="false">
              <v-icon color="grey lighten-1">mdi-information</v-icon>
            </v-btn>
          </v-list-item-action>
        </v-list-item>
      </v-list>
    </v-card-text>
    <v-card-text
      v-else-if="filter"
      class="grow d-flex justify-center align-center grey--text py-5"
    >No files or folders found</v-card-text>
    <v-card-text
      v-else
      class="grow d-flex justify-center align-center grey--text py-5"
    >The folder is empty</v-card-text>
    <v-divider v-if="path"></v-divider>
    <v-toolbar v-if="false && path && isFile" dense flat class="shrink">
      <v-btn icon>
        <v-icon>mdi-download</v-icon>
      </v-btn>
    </v-toolbar>
    <v-toolbar v-if="path && isDir" dense flat class="shrink">
      <v-text-field
        solo
        flat
        hide-details
        label="Filter"
        v-model="filter"
        prepend-inner-icon="mdi-filter-outline"
        class="ml-n3"
      />
      <v-btn icon v-if="false">
        <v-icon>mdi-eye-settings-outline</v-icon>
      </v-btn>
      <v-btn icon @click="load">
        <v-icon>mdi-refresh</v-icon>
      </v-btn>
    </v-toolbar>
  </v-card>
</template>

<script lang="ts">
import formatBytes from '@/utils/formatBytes';
import Confirm from './Confirm.vue';
import Vue, { PropType } from 'vue';
import { Icons, TreeItem } from '@/types';

export default Vue.extend({
  props: {
    icons: {
      type: Object as PropType<Icons>,
    },
    baseUrl: {
      type: String,
    },
    path: {
      type: String,
    },
    refreshPending: Boolean,
  },
  components: {
    Confirm,
  },
  data () {
    return {
      items: [] as TreeItem[],
      filter: '',
    };
  },
  computed: {
    dirs (): TreeItem[] {
      return this.items.filter(
        item => item.is_directory && item.name.includes(this.filter),
      );
    },
    files (): TreeItem[] {
      return this.items.filter(
        item =>
          !item.is_directory && item.name.includes(this.filter),
      );
    },
    isDir (): boolean {
      return this.path[this.path.length - 1] === '/';
    },
    isFile (): boolean {
      return !this.isDir;
    },
  },
  methods: {
    formatBytes,
    changePath (path: string) {
      this.$emit('path-changed', path);
    },
    async load () {
      this.$emit('loading', true);
      if (this.isDir) {
        const url = `${this.baseUrl}/dir${this.path}`;

        try {
          const response = await fetch(url);
          if (!response.ok) {
            throw await response.text();
          }
          const data = await response.json();
          this.items = data;
        } catch (error) {
          console.error(error);
          alert('An error occured. Check the console');
        }
      } else {
        // TODO: load file
      }
      this.$emit('loading', false);
    },
    async deleteItem (item: TreeItem) {
      const dialog = this.$refs.confirm as InstanceType<typeof Confirm>;
      const confirmed = await dialog.open('Delete',
        `Are you sure<br>you want to delete this ${
          item.is_directory ? 'folder' : 'file'
        }?<br><em>${item.name}</em>`,
      );

      if (!confirmed) {
        return;
      }
      this.$emit('loading', true);
      const url = `${this.baseUrl}/file/${item.path}`;

      try {
        const res = await fetch(url, {
          method: 'delete',
        });
        if (!res.ok) {
          throw await res.text();
        }
        this.$emit('file-deleted');
      } catch (error) {
        console.error(error);
        alert('An error occured. Check the console');
      }
      this.$emit('loading', false);
    },
  },
  watch: {
    async path () {
      this.items = [];
      await this.load();
    },
    async refreshPending () {
      if (this.refreshPending) {
        await this.load();
        this.$emit('refreshed');
      }
    },
  },
});
</script>

<style lang="scss" scoped>
.v-card {
    height: 100%;
}
</style>
