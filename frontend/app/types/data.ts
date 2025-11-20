export interface Owner {
  id: string;
  name: string;
  email: string;
  phone: string;
}

export interface OwnerCreateData {
  name: string;
  email: string;
  phone: string;
}

export interface OwnerListProps {
  fetchTrigger: number;
  onEdit: (owner: Owner) => void
}

export interface OwnerFormProps {
  onOwnerUpdated: () => void;
  initialData?: Owner | null; 
  onCancelEdit: () => void;
}

export interface FastAPIError {
  detail: string | any[] | object;
}

export interface Asset {
  id: string;
  name: string;
  category: string;
  owner_id: string;
  owner_ref?: Owner; 
}

export interface AssetCreateData {
  name: string;
  category: string;
  owner_id: string; 
}

export interface AssetListProps {
  fetchTrigger: number;
  onEdit: (asset: Asset) => void
}

export interface AssetFormProps {
  onAssetUpdated: () => void;
  initialData?: Asset | null; 
  onCancelEdit: () => void;
}

export interface BaseFormProps {
    onSubmitted?: () => void; 
}