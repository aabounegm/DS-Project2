export type Item = {
  type: 'file' | 'dir';
  path: string;
  name: string;
}

export type Icons = Record<string, string>;

export type MyFile = {
  name: string,
  type: string,
  size: number,
  extension?: string,
  preview: string,
};

export type Remote = {
  name: string,
  url: string,
  icon?: string,
};


type TreeFile = {
  is_directory: false;
  extension: string;
  size: number;
  replicas: number;
};

type TreeDir = {
  is_directory: true;
  children: TreeItem[];
}

export type TreeItem = {
  name: string;
  path: string;
} & (TreeFile | TreeDir);
